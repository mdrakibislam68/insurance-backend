from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from loguru import logger
Account = get_user_model()


@shared_task(bind=True)
def execute_scheduled_process_action(self, scheduled_action_id, context=None, performer_id=None):
    from .models import ScheduledProcessAction
    from .services.process_actions_service import ProcessActionService

    action_performer = Account.objects.filter(id=performer_id).first()

    try:
        scheduled_action = ScheduledProcessAction.objects.get(id=scheduled_action_id)

        if scheduled_action.status == 'completed':
            logger.warning(f"Scheduled action {scheduled_action_id} is already completed.")
            return

        if scheduled_action.scheduled_job.process.status == 'disabled':
            logger.warning(f"Process is already disabled.")
            return

        if scheduled_action.process_action.status == 'disabled':
            logger.warning(f"Process action is already disabled.")
            return

        # Update the task_id in the model
        scheduled_action.task_id = self.request.id
        scheduled_action.save()

        action_service = ProcessActionService()
        action_service.run_action(
            job=scheduled_action.scheduled_job,
            action=scheduled_action.process_action,
            context=context,
            action_performer=action_performer
        )

        # Mark as completed
        scheduled_action.status = 'completed'
        scheduled_action.last_run_time = now()
        scheduled_action.save()

        logger.success(f"Successfully executed scheduled action {scheduled_action_id}")

        if not ScheduledProcessAction.objects.filter(scheduled_job=scheduled_action.scheduled_job,
                                                     status='pending').exists():
            scheduled_action.scheduled_job.status = 'completed'
            scheduled_action.scheduled_job.save()

        return scheduled_action.process_action.action_type

    except ScheduledProcessAction.DoesNotExist:
        logger.error(f"ScheduledProcessAction with ID {scheduled_action_id} does not exist.")
        self.update_state(state='FAILED', meta={"error": "ScheduledProcessAction does not exist"})
    except Exception as e:
        logger.exception(f"Error executing scheduled action {scheduled_action_id}: {e}")
        # Update status to failed and log the error
        scheduled_action.status = 'failed'
        scheduled_action.error_message = str(e)
        scheduled_action.save()
        self.update_state(state='FAILURE', meta={"error": str(e)})


# @shared_task
# def execute_process_action(action_id, schedule_id, context=None):
#     from .services.process_actions_service import ProcessActionService
#     try:
#         action_service = ProcessActionService()
#         action = ProcessAction.objects.get(id=action_id, status='active')
#         job = ScheduledJob.objects.get(id=schedule_id)
#         action_service.run_action(job=job, action=action, context=context)
#         logger.success(f'Executed process action {action_id} | ActionType {action.action_type}')
#     except ProcessAction.DoesNotExist:
#         logger.error(f"ProcessAction with ID {action_id} does not exist.")
#     except ScheduledJob.DoesNotExist:
#         logger.error(f"Action Task: ScheduledJob with ID {schedule_id} does not exist.")
#     except Exception as e:
#         logger.error(f"Action Task: Error executing process action {action_id}: {str(e)}")
#
#
# @shared_task
# def run_scheduled_job(job_id, run_now=False, context=None):
#     from .services.process_service import ProcessService
#     """
#     Celery task to execute the scheduled job for a process.
#     """
#     try:
#         job = ScheduledJob.objects.get(id=job_id)
#         if job:
#             if run_now:
#                 job.scheduledactiontrack_set.all().delete()
#             job.run_logs = {
#                 "id": str(uuid.uuid4())[:8],
#                 "run_datetime_utc": now().strftime("%Y-%m-%d %H:%M:%S"),
#             }
#             job.save()
#             process_service = ProcessService(event_type=job.process.event_type, context=context)
#             process_service.set_objects(job.object_id)
#             process_service.execute_actions(job.process, job_id, run_now)
#
#             job.status = 'completed'
#             job.save()
#             logger.success(f"Scheduled job {job_id} executed successfully.")
#     except ScheduledJob.DoesNotExist as e:
#         # Log the error
#         logger.error(f"Schedule Task: Error executing scheduled job {job_id}: {str(e)}")
