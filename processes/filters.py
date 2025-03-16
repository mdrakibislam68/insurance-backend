from django_filters import rest_framework as filters
from processes.models import ScheduledJob, ActivityLogs


class ScheduledJobFilter(filters.FilterSet):
    min_date = filters.DateTimeFilter(field_name="run_time", lookup_expr='gte')
    max_date = filters.DateFilter(method="run_time_max")
    event_type = filters.CharFilter(field_name="process__event_type", lookup_expr='icontains')


    class Meta:
        model = ScheduledJob
        fields = ['event_type', 'process_id', 'object_id', 'status', 'min_date', 'max_date']

    def run_time_max(self, queryset, name, value):
        queryset = queryset.filter(
                run_time__lte=f'{value} 23:59:59'
            )
        return queryset

class ActivityLogsFilter(filters.FilterSet):
    min_date = filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    max_date = filters.DateFilter(method="time_max")
    email = filters.CharFilter(field_name="user__email", lookup_expr='icontains')

    class Meta:
        model = ActivityLogs
        fields = ['action_type', 'email', 'min_date', 'max_date']

    def time_max(self, queryset, name, value):
        queryset = queryset.filter(
                created_at__lte=f'{value} 23:59:59'
            )
        return queryset
