from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from processes.models import Process, ProcessAction, ScheduledJob, ScheduledActionTrack, ActivityLogs

Account = get_user_model()


class ProcessActionCreateOrUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessAction
        exclude = ['created_at', 'updated_at']


class ProcessActionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessAction
        exclude = ['created_at', 'updated_at', 'process']


class ProcessListSerializer(serializers.ModelSerializer):
    actions = ProcessActionListSerializer(many=True, required=False, source='processaction_set')

    class Meta:
        model = Process
        exclude = ['created_at', 'updated_at']


class ProcessSerializer(serializers.ModelSerializer):
    actions = ProcessActionListSerializer(many=True, required=False)

    class Meta:
        model = Process
        exclude = ['created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        actions_data = validated_data.pop('actions', [])
        process = Process.objects.create(**validated_data)

        # Create ProcessAction instances
        for action_data in actions_data:
            ProcessAction.objects.create(**action_data, process=process)

        return process


class ProcessShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['id', 'name', 'event_type']


class ProcessUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        exclude = ['created_at', 'updated_at']


class ChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class ChoicesSerializer(serializers.Serializer):
    event_type_options = ChoiceSerializer(many=True)
    action_type_options = ChoiceSerializer(many=True)


class JobActionsSerializer(serializers.ModelSerializer):
    action_type = serializers.CharField(read_only=True, source='get_action_type_display')

    class Meta:
        model = ProcessAction
        fields = ['action_type']


class ScheduledActionTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledActionTrack
        exclude = ['created_at', 'action', 'schedule', 'id']


class ScheduledJobListSerializer(serializers.ModelSerializer):
    event = serializers.CharField(source='process.get_event_type_display')
    process_name = serializers.CharField(source='process.name')
    actions = JobActionsSerializer(source='process.processaction_set', many=True)
    run_logs = serializers.JSONField()
    run_action__logs = ScheduledActionTrackSerializer(many=True, source='scheduledactiontrack_set')

    class Meta:
        model = ScheduledJob
        exclude = ['created_at', 'updated_at', 'process', 'task_id']


class PaginatedScheduledJobResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = ScheduledJobListSerializer(many=True)


class ProcessOptionSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='name', read_only=True)
    value = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Process
        fields = ['id', 'label', 'value']


class ProcessActionTestSerializer(serializers.Serializer):
    action = serializers.PrimaryKeyRelatedField(queryset=ProcessAction.objects.all())


class ScheduleJobHandleActionSerializer(serializers.Serializer):
    action_type = serializers.ChoiceField(
        choices=[('cancel', 'Cancel'), ('run_now', 'Run Now'), ('run_again', 'Run Again')])


class MailchimpAudienceOptionList(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    label = serializers.CharField(source='name', read_only=True)
    value = serializers.CharField(source='id', read_only=True)


class ActionPerformerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'email', 'is_staff']


class ActivityLogsListSerializer(serializers.ModelSerializer):
    action_type = serializers.CharField(source='get_action_type_display')
    actions = JobActionsSerializer(source='action_track.process.processaction_set', many=True, read_only=True)
    run_logs = serializers.JSONField(source='action_track.run_logs', read_only=True)
    run_action__logs = ScheduledActionTrackSerializer(many=True, source='action_track.scheduledactiontrack_set',
                                                      read_only=True)
    user = ActionPerformerAccountSerializer()

    class Meta:
        model = ActivityLogs
        exclude = ['updated_at', 'action_track']


class PaginatedActivityLogsResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = ActivityLogsListSerializer(many=True)
