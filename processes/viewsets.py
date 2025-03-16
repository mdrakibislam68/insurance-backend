from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from common_bases.permissions import IsAdminOrHasPermission
from common_bases.serializers import EmptySerializer
from common_bases.viewsets import InitialModelViewSet
from processes.filters import ScheduledJobFilter, ActivityLogsFilter
from processes.models import Process, ProcessAction, ScheduledJob, ActivityLogs
from processes.serializers import ChoicesSerializer, ProcessSerializer, ProcessActionCreateOrUpdateSerializer, \
    ProcessUpdateSerializer, ScheduledJobListSerializer, PaginatedScheduledJobResponseSerializer, ProcessListSerializer, \
    ProcessOptionSerializer, ProcessActionTestSerializer, ScheduleJobHandleActionSerializer, \
    MailchimpAudienceOptionList, \
    PaginatedActivityLogsResponseSerializer, ActivityLogsListSerializer, ChoiceSerializer
from processes.services.process_service import cancel_scheduled_job, \
    run_scheduled_job_now, run_scheduled_job_again
from utils.paginations import StandardResultsSetPagination


class ProcessViewSets(InitialModelViewSet):
    queryset = Process.objects.all()

    required_permissions = []

    def get_permissions(self):
        if self.action in ['list']:
            self.required_permissions = ['processes.api_read_processes']
            self.permission_classes = [IsAdminOrHasPermission]
        elif self.action in ['create', 'create_process_action']:
            self.required_permissions = ['processes.api_create_processes']
            self.permission_classes = [IsAdminOrHasPermission]
        elif self.action in ['update', 'update_process_action']:
            self.required_permissions = ['processes.api_edit_processes']
            self.permission_classes = [IsAdminOrHasPermission]
        elif self.action in ['destroy', 'delete_process_action']:
            self.required_permissions = ['processes.api_delete_processes']
            self.permission_classes = [IsAdminOrHasPermission]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action == 'list':
            return ProcessListSerializer
        elif self.action == 'create':
            return ProcessSerializer
        elif self.action == 'update':
            return ProcessUpdateSerializer
        elif self.action in ['create_process_action', 'update_process_action']:
            return ProcessActionCreateOrUpdateSerializer
        elif self.action == 'type_option_list':
            return ChoicesSerializer
        elif self.action == 'process_option_list':
            return ProcessOptionSerializer
        elif self.action == 'process_action_test':
            return ProcessActionTestSerializer
        elif self.action == 'mailchimp_audience_list':
            return MailchimpAudienceOptionList
        return EmptySerializer

    @extend_schema(
        request=None,
        responses={
            200: ProcessListSerializer(many=True),
        },
        operation_id='process_list',
        tags=['Processes'],
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ProcessSerializer,
        responses={
            200: None,
        },
        operation_id='create_process',
        tags=['Processes'],
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'New process created successfully!'})

    @extend_schema(
        request=ProcessUpdateSerializer,
        responses={
            200: None,
        },
        operation_id='update_process',
        tags=['Processes'],
    )
    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Process updated successfully!'})

    @extend_schema(
        request=None,
        responses={
            200: None,
        },
        operation_id='delete_process',
        tags=['Processes'],
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Process deleted successfully!'})

    @extend_schema(
        request=ProcessActionCreateOrUpdateSerializer,
        responses={
            200: None,
        },
        operation_id='create_process_action',
        tags=['Processes'],
    )
    @action(detail=False, methods=['POST'], name='Create process action', url_path='create-process-action')
    def create_process_action(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'New process action created successfully!'})

    @extend_schema(
        request=ProcessActionCreateOrUpdateSerializer,
        responses={
            200: None,
        },
        operation_id='update_process_action',
        tags=['Processes'],
    )
    @action(detail=False, methods=['PUT'], name='Update Process Action',
            url_path='update-process-action/(?P<action_id>\\d+)')
    def update_process_action(self, request, action_id=None):
        instance = get_object_or_404(ProcessAction, id=action_id)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Action updated successfully!'})

    @extend_schema(
        request=None,
        responses={
            200: None,
        },
        operation_id='delete_process_action',
        tags=['Processes'],
    )
    @action(detail=False, methods=['DELETE'], name='Delete Process Action',
            url_path='delete-process-action/(?P<action_id>\\d+)')
    def delete_process_action(self, request, action_id=None):
        instance = get_object_or_404(ProcessAction, id=action_id)
        instance.delete()
        return Response({'message': 'Action deleted successfully!'})

    @extend_schema(
        request=None,
        responses={
            200: ChoicesSerializer,
        },
        operation_id='type_option_list',
        tags=['Processes'],
    )
    @action(detail=False, methods=['GET'], name='Process and ProcessAction Options List', url_path='type-option-list')
    def type_option_list(self, request, *args, **kwargs):
        event_type_options = [
            {'value': choice[0], 'label': choice[1]} for choice in Process.EVENT_TYPE_CHOICES
        ]
        action_type_options = [
            {'value': choice[0], 'label': choice[1]} for choice in ProcessAction.ACTION_TYPE_CHOICES
        ]
        data = {
            'event_type_options': event_type_options,
            'action_type_options': action_type_options
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)

    @extend_schema(
        request=None,
        responses={
            200: ProcessOptionSerializer(many=True),
        },
        operation_id='process_option_list',
        tags=['Processes'],
    )
    @action(detail=False, methods=['GET'], name='Process Options List', url_path='process-option-list')
    def process_option_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ScheduledJobViewSets(InitialModelViewSet):
    queryset = ScheduledJob.objects.all().order_by('-created_at')
    permission_classes = [IsAdminUser]
    filterset_class = ScheduledJobFilter
    custom_pagination = StandardResultsSetPagination()
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action == 'handle_action':
            return ScheduleJobHandleActionSerializer
        return ScheduledJobListSerializer

    @extend_schema(
        request=None,
        responses={
            200: PaginatedScheduledJobResponseSerializer,
        },
        parameters=[
            OpenApiParameter(name='page', description='Result page number', required=False, type=int,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='page_size', description='Result page size', required=False, type=int,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='event_type', description='Filter by event type', required=False,
                             type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='process_id', description='Filter by process', required=False, type=int,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='object_id', description='Filter by object id', required=False, type=int,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='status', description='Filter by status', required=False, type=str,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='max_date', description='Filter by max date', required=False,
                             type=OpenApiTypes.DATETIME, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='min_date', description='Filter by min date', required=False,
                             type=OpenApiTypes.DATETIME, location=OpenApiParameter.QUERY)
        ],
        operation_id='scheduled_job_list',
        tags=['ScheduledJobs'],
    )
    @action(detail=False, methods=['GET'], name='Scheduled Job List', url_path='paginated-scheduled-job-list')
    def scheduled_job_list(self, request):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        result_page = self.custom_pagination.paginate_queryset(queryset, request)
        serializer = self.get_serializer(result_page, many=True)
        return self.custom_pagination.get_paginated_response(serializer.data)

    @extend_schema(
        request=ScheduleJobHandleActionSerializer,
        responses={
            200: None,
        },
        operation_id='handle_action',
        tags=['ScheduledJobs'],
    )
    @action(detail=True, methods=['POST'], name='Scheduled jobs handle actions', url_path='handle-action')
    def handle_action(self, request, pk=None):
        instance = self.get_object()
        action_performer = request.user
        serializer = ScheduleJobHandleActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('action_type') == 'cancel':
            action_execute = cancel_scheduled_job(instance, action_performer)
        elif serializer.validated_data.get('action_type') == 'run_now':
            action_execute = run_scheduled_job_now(instance, action_performer)
        elif serializer.validated_data.get('action_type') == 'run_again':
            action_execute = run_scheduled_job_again(instance, action_performer)
        else:
            return Response({"non_field_errors": ["Action failed to perform!"]}, status=status.HTTP_400_BAD_REQUEST)
        if action_execute[0]:
            return Response({'message': action_execute[1]})
        return Response({"non_field_errors": [action_execute[1]]}, status=status.HTTP_400_BAD_REQUEST)


class ActivityLogsViewSets(InitialModelViewSet):
    queryset = ActivityLogs.objects.select_related('action_track').all().order_by('-created_at')
    filterset_class = ActivityLogsFilter
    custom_pagination = StandardResultsSetPagination()
    filter_backends = [DjangoFilterBackend]

    required_permissions = []

    def get_permissions(self):
        if self.action == 'activity_logs_list':
            self.required_permissions = ['processes.api_read_activitylogs']
            self.permission_classes = [IsAdminOrHasPermission]
        elif self.action == 'clear_activity_logs':
            self.required_permissions = ['processes.api_delete_activitylogs']
            self.permission_classes = [IsAdminOrHasPermission]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action == 'action_option_list':
            return ChoiceSerializer
        elif self.action == 'activity_logs_list':
            return ActivityLogsListSerializer
        return EmptySerializer

    @extend_schema(
        request=None,
        responses={
            200: ChoiceSerializer(many=True),
        },
        operation_id='action_option_list',
        tags=['ActivityLogs'],
    )
    @action(detail=False, methods=['GET'], name='Activity logs action List', url_path='action-option-list')
    def action_option_list(self, request, *args, **kwargs):
        data = [
            {'value': choice[0], 'label': choice[1]} for choice in ActivityLogs.EVENT_TYPES
        ]
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=None,
        responses={
            200: PaginatedActivityLogsResponseSerializer,
        },
        parameters=[
            OpenApiParameter(name='page', description='Result page number', required=False, type=int,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='page_size', description='Result page size', required=False, type=int,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='action_type', description='Filter by action type', required=False,
                             type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='email', description='Filter by user email', required=False,
                             type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='user_id', description='Filter by user', required=False, type=int,
                             location=OpenApiParameter.QUERY),
            OpenApiParameter(name='max_date', description='Filter by max date', required=False,
                             type=OpenApiTypes.DATETIME, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='min_date', description='Filter by min date', required=False,
                             type=OpenApiTypes.DATETIME, location=OpenApiParameter.QUERY)
        ],
        operation_id='activity_logs_list',
        tags=['ActivityLogs'],
    )
    @action(detail=False, methods=['GET'], name='Activity Logs List', url_path='paginated-activity-logs-list')
    def activity_logs_list(self, request):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        result_page = self.custom_pagination.paginate_queryset(queryset, request)
        serializer = self.get_serializer(result_page, many=True)
        return self.custom_pagination.get_paginated_response(serializer.data)

    @extend_schema(
        request=None,
        responses={
            200: None,
        },
        operation_id='clear_activity_logs',
        tags=['ActivityLogs'],
    )
    @action(detail=False, methods=['POST'], name='Clear Activity Logs', url_path='clear-activity-logs')
    def clear_activity_logs(self, request, *args, **kwargs):
        queryset = ActivityLogs.objects.all()
        queryset.delete()
        return Response({'message': 'Activity logs cleared successfully!'})
