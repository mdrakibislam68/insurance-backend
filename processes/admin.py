from django.contrib import admin
from .models import ProcessAction, Process

# Register your models here.

class ProcessActionInline(admin.TabularInline):
    model = ProcessAction
    extra = 1


class ProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = [ProcessActionInline]

    class Meta:
        model = Process
        fields = '__all__'
        verbose_name = 'Process'
        verbose_name_plural = 'Processes'
        ordering = ('id',)
        filter_horizontal = ()
        search_fields = ('name', 'action', 'status')
        date_hierarchy = 'date'


admin.site.register(Process, ProcessAdmin)
