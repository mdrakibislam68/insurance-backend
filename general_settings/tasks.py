from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def task_test_email(to_email, from_email=settings.DEFAULT_FROM_EMAIL):
    send_mail(
        'Subject here',
        'Here is the message.',
        from_email,
        [to_email],
    )
