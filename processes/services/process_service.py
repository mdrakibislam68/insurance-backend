import uuid
from datetime import timedelta

from celery.result import AsyncResult
from django.utils import timezone
from django.utils.timezone import now

from processes.models import Process, ScheduledJob, ActivityLogs, ScheduledProcessAction
from processes.tasks import execute_scheduled_process_action


class ProcessService:
    def __init__(self, event_type, event_time=None, booking=None, transition=None, customer=None, context=None):
        self.event_type = event_type
        self.booking = booking
        self.transition = transition
        self.customer = customer
        self.context = context
        self.processes = Process.objects.filter(event_type=event_type, status='active')
        self.event_time = event_time if event_time else timezone.now()

    def make_context(self, changes):
        """
        Create a context dictionary containing relevant details from booking and transaction.
        This context is used to evaluate conditions.
        """
        context = {
            "status": self.booking.status if self.booking else "",
            "session": self.booking.service.id if self.booking else "",
            "agent": self.booking.agent.id if self.booking else "",
            "payment_status": self.booking.payment_status if self.booking else "",
            "payment_method": self.transition.method if self.transition else "",
            "payment_portion": self.transition.payment_portion if self.transition else "",
            "fund_status": self.transition.fund_status if self.transition else "",
            "transaction_status": self.transition.status if self.transition else "",
            "start_time_changed": False,
            "session_changed": False,
            "agent_changed": False,
            "status_changed": False,
            "payment_status_changed": False,
            "old_session": "",
            "old_agent": "",
            "old_status": "",
            "old_payment_status": "",
            "referrer": self.customer.referrer_details.exists() if self.customer else None,
            "referrer_customer": self.booking.customer.referrer_details.exists() if self.booking and self.booking.customer else None,
            "customer_first_booking": self.booking.customer.booking_set.count() == 1 if self.booking and self.booking.customer else None
        }
        if changes:
            for field, change in changes.items():
                if field == 'service':
                    field = 'session'

                if field == 'start_datetime':
                    context['start_time_changed'] = True

                if f"{field}_changed" in context:
                    context[f"{field}_changed"] = True

                if field in ['session', 'agent']:
                    context[f"old_{field}"] = change.get('old').id
                elif f"old_{field}" in context:
                    context[f"old_{field}"] = change.get('old')
        return context

    def run_process(self, changes=None, run_now=False):
        """
        Evaluate and run processes based on the provided conditions and context.
        """
        if self.event_type not in ['time_slot_released', 'waiting_list_subscribe', 'waiting_list_unsubscribe']:
            context = self.make_context(changes)
        else:
            context = {}

        # Iterate through all active processes for the current event type
        for process in self.processes:
            if process.is_conditional:
                # Evaluate conditions and continue to next process if conditions are not met
                if not self.evaluate_conditions(process.condition, context):
                    continue
            # Schedule or update the process
            self.schedule_or_update_job(process, run_now)

    def evaluate_conditions(self, conditions, context):
        """
        Evaluate a list of conditions against the provided context.
        Conditions can be chained using 'and'/'or' logic.
        """
        result = None
        for condition in conditions:
            if condition["comparison"] in ['changed', 'not_changed']:
                target_value = context.get(f"{condition['target_props']}_changed")
            elif condition["comparison"] in ['was_equal', 'was_not_equal']:
                target_value = context.get(f"old_{condition['target_props']}")
            # elif condition["comparison"] == 'not_null':
            #     target_value = context.get(condition['target_props']) is not None
            else:
                target_value = context.get(condition['target_props'])
            value = condition['value']
            if condition["comparison"] == 'changed':
                value = True
            elif condition["comparison"] == 'not_changed':
                value = False
            elif condition["comparison"] in ['equal']:
                value = [True if val == 'is_true' else False for val in condition['value'] if
                         val in ['is_true', 'is_false']]

            # Compare the values using the comparison method

            condition_met = self.compare_values(target_value, condition['comparison'], value)

            # Combine the result with previous conditions using AND/OR logic
            result = condition_met
            if not condition_met:
                break
        return result

    def compare_values(self, target_value, comparison, value):

        """
        Compare the target_value against the condition's expected value using the specified comparison type.
        Supported comparison types:
        - eq_in: Equal to one of the values in a list
        - neq_in: Not equal to any of the values in a list
        - has_changed: Value has changed
        - has_not_changed: Value has not changed
        """
        if comparison in ['eq_in', 'was_equal', 'equal']:
            return target_value in value
        elif comparison in ['neq_in', 'was_not_equal', 'not_equal']:
            return target_value not in value
        elif comparison in ['changed']:
            return target_value == value
        elif comparison == 'not_changed':
            return target_value != value
        else:
            # Add more comparisons as needed (e.g., greater_than, less_than)
            return False

    def get_offset_time(self, time_offset):
        """
        Calculate the future execution time for the scheduled process based on the provided time offset.
        """
        time_offset_value = time_offset.get('time_offset_value')
        time_offset_unit = time_offset.get('time_offset_unit')
        time_offset_after_before = time_offset.get('time_offset_after_before')

        offset_time = self.event_time

        if time_offset_value and time_offset_unit and time_offset_after_before:
            time_delta = timedelta()

            if time_offset_unit == 'minutes':
                time_delta = timedelta(minutes=int(time_offset_value))
            elif time_offset_unit == 'hours':
                time_delta = timedelta(hours=int(time_offset_value))
            elif time_offset_unit == 'days':
                time_delta = timedelta(days=int(time_offset_value))

            if time_offset_after_before == 'after':
                offset_time = self.event_time + time_delta
            elif time_offset_after_before == 'before':
                offset_time = self.event_time - time_delta

        return offset_time

    def schedule_or_update_job(self, process, run_now=False):
        object_id = self._get_object_id(process)
        run_time = self.get_offset_time(process.time_offset)

        # Check if a job already exists for this process and object
        existing_job = self.get_scheduled_job(process, object_id)

        if not existing_job:
            # Create a new ScheduledJob
            existing_job = ScheduledJob.objects.create(
                process=process,
                object_id=object_id,
                status='scheduled',
                run_time=run_time,
            )

        existing_job.run_logs = {
            "id": str(uuid.uuid4())[:8],
            "run_datetime_utc": run_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        existing_job.status = 'scheduled'
        existing_job.run_time = run_time
        existing_job.save()

        # Create or update ScheduledProcessAction for each action
        for action in process.processaction_set.filter(status='active'):
            scheduled_action, created = ScheduledProcessAction.objects.get_or_create(
                scheduled_job=existing_job,
                process_action=action,
            )

            # Check if there is an existing task
            if scheduled_action.task_id:
                # Revoke the existing task
                AsyncResult(scheduled_action.task_id).revoke(terminate=True)

                # Update the status to 'pending'
                scheduled_action.status = 'pending'
                scheduled_action.task_id = None  # Clear the old task ID
                scheduled_action.save()

            # Schedule the action
            if run_now:
                task = execute_scheduled_process_action.delay(scheduled_action.id, self.context)
            else:
                # Schedule the action for future execution
                task = execute_scheduled_process_action.apply_async(
                    args=[scheduled_action.id, self.context],
                    eta=run_time,
                )
            # Update the task ID and save
            scheduled_action.task_id = task.id
            scheduled_action.save()

    @staticmethod
    def get_scheduled_job(process, object_id):
        """
        Check if a ScheduledJob already exists for this process and object.
        """
        try:
            return ScheduledJob.objects.get(process=process, object_id=object_id)
        except ScheduledJob.DoesNotExist:
            return None

    def _get_object_id(self, process):
        """
        Retrieve the object_id based on the event type.
        This can refer to booking, customer, or transition objects.
        """
        if self.event_type in ['booking_created', 'booking_updated', 'booking_start', 'booking_end',
                               'time_slot_released', 'waiting_list_subscribe', 'waiting_list_unsubscribe']:
            return self.booking.id
        elif self.event_type in ['customer_created', 'customer_created_from_dashboard']:
            return self.customer.id
        elif self.event_type in ['transaction_created', 'transaction_updated']:
            return self.transition.id
        else:
            return None

    @staticmethod
    def get_objects(object_id, process_type):
        booking = None
        customer = None
        transition = None

        # if process_type in ['booking_created', 'booking_updated', 'booking_start', 'booking_end']:
        #     booking = Booking.objects.get(id=object_id)
        # elif process_type in ['customer_created', 'customer_created_from_dashboard']:
        #     customer = Customer.objects.get(id=object_id)
        # elif process_type in ['transaction_created', 'transaction_updated']:
        #     transition = Transaction.objects.get(id=object_id)
        return booking, customer, transition

    def set_objects(self, object_id):
        self.booking, self.customer, self.transition = self.get_objects(object_id=object_id,
                                                                        process_type=self.event_type)


########## Individual functions ##########
def trigger_process(event_type, event_time=None, changes=None, booking=None, transition=None,
                    customer=None, run_now=None, context=None):
    process_service = ProcessService(event_type=event_type, event_time=event_time, booking=booking,
                                     transition=transition, customer=customer, context=context)
    process_service.run_process(changes, run_now)


def cancel_scheduled_job(job, action_performer):
    """
    Cancels all actions linked to a ScheduledJob by revoking their tasks
    and updating their statuses to 'cancelled'.
    """
    actions = ScheduledProcessAction.objects.filter(scheduled_job=job)
    for item in actions:
        if item.task_id:
            # Revoke the Celery task if it exists
            AsyncResult(item.task_id).revoke(terminate=True)

        # Update the status to 'cancelled' and save the changes
        item.status = 'cancelled'
        item.save()

    # Update the job status to 'cancelled' if all actions are cancelled
    job.status = 'cancelled'
    job.save()

    # Log the cancellation
    ActivityLogs.objects.create(
        action_type='process_job_cancelled',
        action_track=job,
        user=action_performer
    )

    return True, f"All actions for Job {job.id} have been successfully cancelled."


def run_scheduled_job_now(job, action_performer):
    """
    Immediately execute a scheduled job.
    """
    if job.status == 'scheduled':
        # run_scheduled_job(job_id=job.id, run_now=True)
        actions = ScheduledProcessAction.objects.filter(scheduled_job=job)
        for item in actions:
            if item.task_id:
                AsyncResult(item.task_id).revoke(terminate=True)
            item.status = 'pending'
            item.task_id = None
            item.save()
            task = execute_scheduled_process_action.delay(item.id, None, action_performer.id)
            item.task_id = task.id
            item.save()
        ActivityLogs.objects.create(
            action_type='process_job_run',
            action_track=job,
            user=action_performer
        )
        job.status = 'completed'
        job.run_time = now()
        job.run_logs = {
            "id": str(uuid.uuid4())[:8],
            "run_datetime_utc": now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        job.save()
        return True, f"Job {job.id} is now running."
    else:
        return False, f"Job {job.id} is not in a scheduled state."


def run_scheduled_job_again(job, action_performer):
    """
    Re-run a completed or previously scheduled job.
    """
    if job.status == 'completed':
        actions = ScheduledProcessAction.objects.filter(scheduled_job=job)
        for item in actions:
            if item.task_id:
                AsyncResult(item.task_id).revoke(terminate=True)
            item.status = 'pending'
            item.task_id = None
            item.save()
            task = execute_scheduled_process_action.delay(item.id, None, action_performer.id)
            item.task_id = task.id
            item.save()
        ActivityLogs.objects.create(
            action_type='process_job_run',
            action_track=job,
            user=action_performer
        )
        job.status = 'completed'
        job.run_time = now()
        job.run_logs = {
            "id": str(uuid.uuid4())[:8],
            "run_datetime_utc": now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        job.save()
        return True, f"Job {job.id} is being run again."
    else:
        return False, f"Job {job.id} has not completed yet or cannot be run again."
