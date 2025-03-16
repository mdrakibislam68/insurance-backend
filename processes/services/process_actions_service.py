import abc
import re
import traceback

import pytz
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from general_settings.services.general_settings_service import GeneralSettingsService
from general_settings.services.model_services import get_strf_date_format
from processes.models import ScheduledActionTrack, ActivityLogs


class DynamicTemplateEngine:
    def __init__(self, data):
        """
        Initialize with the dynamic data dictionary.
        This dictionary contains model data like Booking, Customer, etc.
        """
        self.data = data

    def render(self, template):
        """
        Replaces tags like {{booking_id}} with actual values from the data.
        """
        pattern = r"\{\{(.*?)\}\}"
        matches = re.findall(pattern, template)

        for match in matches:
            key = match.strip()
            value = self.data.get(key, "")
            template = template.replace(f"{{{{{key}}}}}", str(value))

        return template


class BaseAction(abc.ABC):
    """
    Base class for actions like sending email, WhatsApp messages, etc.
    Each action must implement the `execute` method.
    """

    @abc.abstractmethod
    def execute(self, context):
        raise NotImplementedError("Subclasses must implement this method.")


class EmailSendAction(BaseAction):
    def execute(self, context):
        """
        Sends an email using the provided context.
        Context includes 'recipient', 'subject', and 'message'.
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        html_version = 'account/email/blank-template.html'
        html_message = render_to_string(html_version, context={'html_content': context.get('message', '')})
        email_subject = context.get('subject', '')
        message = EmailMessage(email_subject, html_message, from_email, [context.get('to_email', '')])
        message.content_subtype = 'html'
        message.send()


class WhatsAppSendAction(BaseAction):
    def execute(self, context):
        """
        Sends a WhatsApp message using the provided context.
        The context should contain the 'recipient' and 'message'.
        """
        # Here you can integrate with your WhatsApp API
        print(f"Sending WhatsApp message to {context['recipient']}: {context['message']}")


class ProcessActionService:
    def __init__(self):
        self.actions = {
            'send_email': EmailSendAction(),
            'whatsapp_send': WhatsAppSendAction(),
        }

    def set_log_action_result(self, job, action, status, message, process_execution_id=None):
        """
        Log the action result (success or failure) into the ScheduledJob's run_logs field.
        If process_execution_id is None, generate a new one. If it's provided and exists in the logs,
        append the action details; otherwise, create a new log entry.
        """

        ScheduledActionTrack.objects.create(
            action=action,
            message=message,
            schedule=job,
            status=status,
        )

    @staticmethod
    def set_process_activity(action_type, job):
        if action_type == 'send_email':
            ActivityLogs.objects.create(
                action_type='email_sent',
                action_track=job
            )
        elif action_type == 'add_to_mailchimp_list':
            ActivityLogs.objects.create(
                action_type='mailchimp_contact_added_to_list',
                action_track=job
            )
        elif action_type == 'send_sms':
            ActivityLogs.objects.create(
                action_type='sms_sent',
                action_track=job
            )

    def execute_action(self, action, job):
        """
        Execute a process action and log the result.
        """
        try:
            # Find the correct action type and execute it
            action_class = self.actions.get(action.action_type)
            if action_class:
                action_class.execute(action)
                self.log_action_result(job, action, 'success', 'Action completed successfully')
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")
        except Exception as e:
            self.log_action_result(job, action, 'failed', str(e))

    def get_model_data(self, booking=None, customer=None, transaction=None, booking_waiting_list=None, context=None):
        """
        Collects dynamic data from models like Booking, Customer, Agent, etc.
        """
        data = {}
        general_setting = GeneralSettingsService()
        customer_portal_url = general_setting.get_dashboard_url()
        tz = pytz.timezone(general_setting.get_booking_setting('time_zone'))
        date_format = general_setting.get_booking_setting('date_format')
        date_format = get_strf_date_format(date_format) if date_format else date_format
        time_system = general_setting.get_booking_setting('time_system')

        if business_info := general_setting.get_business_info():
            logo = general_setting.get_compony_logo_url()
            data.update({
                'business_logo_url': logo if logo else "",
                'business_logo_image': f'<img style="height: 50px; width: auto;" src="{logo}"/>' if logo else "",
                'business_address': business_info.get('company_name', ''),
                'business_phone': business_info.get('business_phone', ''),
                'business_name': business_info.get('business_address', ''),
            })

        if booking:
            start_date = booking.start_datetime.astimezone(tz).date() if booking.start_datetime else ''
            if start_date and date_format:
                start_date = start_date.strftime(date_format)

            end_date = booking.end_datetime.astimezone(tz).date() if booking.end_datetime else ''
            if end_date and date_format:
                end_date = end_date.strftime(date_format)

            start_time = booking.start_datetime.astimezone(tz) if booking.start_datetime else ''
            if start_time and time_system:
                start_time = start_time.strftime("%I:%M%p").lower() if time_system == "12" else start_time.strftime(
                    "%H:%M")

            end_time = booking.end_datetime.astimezone(tz) if booking.end_datetime else ''
            if end_time and time_system:
                end_time = end_time.strftime("%I:%M%p").lower() if time_system == "12" else end_time.strftime("%H:%M")

            data.update({
                'booking_id': booking.id,
                'booking_code': booking.booking_code,
                'start_date': start_date,
                'end_date': end_date,
                'start_time': start_time,
                'end_time': end_time,
                'service_name': booking.service.name if booking.service else '',
                'service_category': booking.service.category.name if booking.service and booking.service.category else '',
                'booking_duration': booking.duration if booking.duration else '',
                'booking_status': booking.status if booking.status else '',
                'total_attendees': booking.total_attendees if booking.total_attendees else '',
                'agent_email': booking.agent.account.email if booking.agent and booking.agent.account else '',
                'agent_full_name': booking.agent.account.get_full_name() if booking.agent and booking.agent.account else '',
                'agent_first_name': booking.agent.account.first_name if booking.agent and booking.agent.account else '',
                'agent_last_name': booking.agent.account.last_name if booking.agent and booking.agent.account else '',
                'agent_phone': booking.agent.account.phone if booking.agent and booking.agent.account else '',
                'agent_display_name': booking.agent.display_name if booking.agent else '',
                'agent_additional_phones': booking.agent.additional_phone if booking.agent else '',
                'agent_additional_emails': booking.agent.additional_email if booking.agent else '',
                'location_name': booking.location.name if booking.location else '',
                'location_display_name': booking.location.display_name if booking.location else '',
                'location_full_address': booking.location.location if booking.location else '',
                'location_email': booking.location.location_email if booking.location else '',
                'location_phone': booking.location.location_phone if booking.location else '',
                'location_additional_emails': booking.location.location_additional_email if booking.location else '',
                'location_additional_phones': booking.location.location_additional_phone if booking.location else '',
                'booking_payment_status': booking.payment_status if booking.payment_status else '',
                'booking_payment_portion': booking.payment_portion if booking.payment_portion else '',
                'booking_payment_method': booking.payment_method if booking.payment_method else '',
                'booking_payment_amount': format(booking.subtotal, ".2f") if booking.subtotal else '',
                'booking_price': f"{booking.booking_price_track.get('total'):.2f}" if booking.booking_price_track and booking.booking_price_track.get(
                    'total') else '',
                'manage_booking_url_customer': f'{customer_portal_url}/?bookingId={booking.id}',
                'manage_booking_url_agent': f'{settings.FRONT_END_URL}/dashboard/bookings/{booking.id}'
            })

        if customer:
            data.update({
                'customer_email': customer.account.email if customer.account else '',
                'customer_full_name': customer.account.get_full_name() if customer.account else '',
                'customer_first_name': customer.account.first_name if customer.account else '',
                'customer_last_name': customer.account.last_name if customer.account else '',
                'customer_phone': customer.account.phone if customer.account else '',
                'customer_notes': customer.note if customer.note else '',
                'referrer_email': customer.referrer_details.first().referrer.account.email if customer.referrer_details.first() else '',
                'referrer_first_name': customer.referrer_details.first().referrer.account.first_name if customer.referrer_details.first() else '',
                'referrer_last_name': customer.referrer_details.first().referrer.account.last_name if customer.referrer_details.first() else '',
            })

        if transaction:
            data.update({
                'transaction_token': transaction.confirmation_code if transaction.confirmation_code else '',
                'transaction_amount': transaction.amount if transaction.amount else '',
                'transaction_processor': transaction.processor if transaction.processor else '',
                'transaction_payment_method': transaction.method if transaction.method else '',
                'transaction_funds_status': transaction.fund_status if transaction.fund_status else '',
                'transaction_status': transaction.status if transaction.status else '',
                'transaction_notes': transaction.notes if transaction.notes else '',
                'transaction_payment_portion': transaction.payment_portion if transaction.payment_portion else '',
            })

        if booking_waiting_list:
            data.update({
                'waiting_list_id': booking_waiting_list.id,
                'total_attendees': booking_waiting_list.total_attendees,
                'customer_name': booking_waiting_list.customer.account.get_full_name() if booking_waiting_list.customer and booking_waiting_list.customer.account else '',
                'customer_email': booking_waiting_list.customer.account.email if booking_waiting_list.customer and booking_waiting_list.customer.account else '',
                'service_name': booking_waiting_list.service.name if booking_waiting_list.service else '',
                'location_name': booking_waiting_list.location.name if booking_waiting_list.location else '',
                'agent_name': booking_waiting_list.agent.account.get_full_name() if booking_waiting_list.agent and booking_waiting_list.agent.account else '',
                'room_name': booking_waiting_list.room.name if booking_waiting_list.room else '',
                'created_at': booking_waiting_list.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S") if booking_waiting_list.created_at else '',
            })
        if context:
            data.update(context)

        return data

    def process(self, action_type, model_data, action, job, get_data=None, booking=None, action_performer=None):
        """
        Processes the action by dynamically rendering the template and executing the action.
        """
        # Step 1: Render the template with model data
        template_engine = DynamicTemplateEngine(model_data)
        content = template_engine.render(action.content)
        to_email = template_engine.render(action.to_email)
        is_booking_event = bool(
            job.process.event_type in ['booking_created', 'booking_updated', 'booking_start',
                                       'booking_end', 'transaction_created', 'transaction_updated'])
        booking_notification = None

        # Step 2: Find the appropriate action

        if action_type == 'send_email':
            subject = template_engine.render(action.subject)
            data = {
                'message': content,
                'to_email': to_email,
                'subject': subject,
                'process_id': action.id,
            }
        else:
            data = {}

        if get_data:
            return data

        action_service = self.actions.get(action_type)

        if action_service:
            # Step 3: Execute the action with the rendered content
            try:
                action_service.execute(data)
                self.set_log_action_result(job, action, 'success', 'Action completed successfully')
                self.set_process_activity(action_type, job)
            except Exception as e:
                traceback.print_exc()
                error_message = str(e)[:250]
                self.set_log_action_result(job, action, 'failed', error_message)
                self.set_process_activity(action_type, job)
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def run_action(self, job, action, context=None, action_performer=None):
        booking = None
        customer = None
        transition = None
        booking_waiting_list = None
        process_type = job.process.event_type

        # if process_type in ['booking_created', 'booking_updated', 'booking_start', 'booking_end']:
        #     booking = Booking.objects.get(id=job.object_id)
        # elif process_type in ['customer_created', 'customer_created_from_dashboard']:
        #     customer = Customer.objects.get(id=job.object_id)
        # elif process_type in ['transaction_created', 'transaction_updated']:
        #     transition = Transaction.objects.get(id=job.object_id)
        #     booking = transition.booking
        #     customer = transition.booking.customer
        # elif process_type in ['time_slot_released', 'waiting_list_subscribe', 'waiting_list_unsubscribe']:
        #     booking_waiting_list = BookingWaitingList.objects.get(id=job.object_id)
        #     customer = booking_waiting_list.customer

        # Make sure to get customer from booking if available

        model_data = self.get_model_data(
            booking=booking, customer=customer, transaction=transition, booking_waiting_list=booking_waiting_list,
            context=context
        )

        # Handle different types of actions
        if action.action_type == 'send_email':
            self.process(action_type='send_email', model_data=model_data, action=action, job=job, booking=booking,
                         action_performer=action_performer)
        elif action.action_type == 'tx_send_whatsapp':
            self.process('whatsapp_send', model_data, action, job, booking)
        elif action.action_type == 'send_sms':
            self.process('send_sms', model_data, action, job, booking)
        elif action.action_type == 'trigger_webhook':
            self.process('trigger_webhook', model_data, action, job, booking)
