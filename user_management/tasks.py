from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


@shared_task
def send_account_activate_email(to, context, from_email=settings.DEFAULT_FROM_EMAIL):
    html_version = 'account/email/email-activate.html'
    html_message = render_to_string(html_version, context=context)
    email_subject = 'Insurace School of Texas | Verify Account'
    message = EmailMessage(email_subject, html_message, from_email, [to])
    message.content_subtype = 'html'
    message.send()


@shared_task
def send_account_reset_password_email(to, context, from_email=settings.DEFAULT_FROM_EMAIL):
    html_version = 'account/email/email-reset-password.html'
    html_message = render_to_string(html_version, context=context)
    email_subject = 'Insurace School of Texas | Reset Password'
    message = EmailMessage(email_subject, html_message, from_email, [to])
    message.content_subtype = 'html'
    message.send()


@shared_task
def send_customer_account_reset_password_email(to, context, from_email=settings.DEFAULT_FROM_EMAIL):
    html_version = 'account/email/email-reset-password-secretkey.html'
    html_message = render_to_string(html_version, context=context)
    email_subject = 'Insurace School of Texas | Reset Password'
    message = EmailMessage(email_subject, html_message, from_email, [to])
    message.content_subtype = 'html'
    message.send()


@shared_task
def send_staff_invitation_email(to, context, from_email=settings.DEFAULT_FROM_EMAIL):
    html_version = 'account/email/staff-invitation.html'
    html_message = render_to_string(html_version, context=context)
    email_subject = 'Insurace School of Texas | Invitation to Join Team'
    message = EmailMessage(email_subject, html_message, from_email, [to])
    message.content_subtype = 'html'
    message.send()


@shared_task
def send_email_update_link(to, context, from_email=settings.DEFAULT_FROM_EMAIL):
    html_version = 'account/email/update-email.html'
    html_message = render_to_string(html_version, context=context)
    email_subject = 'Insurace School of Texas | Update Email'
    message = EmailMessage(email_subject, html_message, from_email, [to])
    message.content_subtype = 'html'
    message.send()
