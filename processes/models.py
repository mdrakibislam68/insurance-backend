from django.contrib.auth import get_user_model
from django.db import models

from common_bases.base_models import BaseModel


# Create your models here.
class Process(BaseModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('disabled', 'Disabled'),
    ]

    EVENT_TYPE_CHOICES = []

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    is_conditional = models.BooleanField(default=False)
    condition = models.JSONField(null=True, blank=True)
    has_time_offset = models.BooleanField(default=False)
    time_offset = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name


class ProcessAction(BaseModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('disabled', 'Disabled'),
    ]

    ACTION_TYPE_CHOICES = [
        ('tx_send_whatsapp', 'Send WhatsApp Message'),
        ('tx_send_push_notification', 'Send Push Notification'),
        ('send_email', 'Send Email'),
        ('send_sms', 'Send SMS'),
        ('trigger_webhook', 'HTTP Request'),
        ('add_to_mailchimp_list', 'Add contact to Mailchimp'),
    ]
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    audience_id = models.CharField(max_length=255, null=True, blank=True)
    to_email = models.CharField(max_length=250, null=True, blank=True)
    subject = models.CharField(max_length=250, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    process = models.ForeignKey('Process', on_delete=models.CASCADE)

    def __str__(self):
        return self.status


class ScheduledJob(BaseModel):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('scheduled', 'Scheduled'),
        ('cancelled', 'Cancelled')
    ]

    process = models.ForeignKey('Process', on_delete=models.CASCADE)
    object_id = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    run_time = models.DateTimeField()
    task_id = models.CharField(max_length=255, null=True, blank=True)
    run_logs = models.JSONField(default=list, null=True, blank=True)  # Track each execution of the job

    def __str__(self):
        return self.task_id


class ScheduledProcessAction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]

    scheduled_job = models.ForeignKey('ScheduledJob', on_delete=models.CASCADE)
    process_action = models.ForeignKey('ProcessAction', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    task_id = models.CharField(max_length=255, null=True, blank=True)  # Store the Celery task ID
    last_run_time = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)


class ScheduledActionTrack(BaseModel):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True)
    message = models.CharField(max_length=250, null=True, blank=True)
    action = models.ForeignKey('ProcessAction', on_delete=models.CASCADE, null=True)
    schedule = models.ForeignKey('ScheduledJob', on_delete=models.CASCADE, null=True)


class ActivityLogs(BaseModel):
    EVENT_TYPES = [
        ('sms_sent', 'SMS Sent'),
        ('email_sent', 'Email Sent'),
        ('process_job_run', 'Process Job Run'),
        ('process_job_cancelled', 'Process Job Cancelled'),
    ]
    action_type = models.CharField(max_length=200, choices=EVENT_TYPES)
    action_view_link = models.CharField(max_length=350, null=True, blank=True)
    action_track = models.ForeignKey(ScheduledJob, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.action_type
