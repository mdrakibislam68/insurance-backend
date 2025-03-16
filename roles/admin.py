from django.contrib import admin
from django.contrib.auth.models import Group

from .models import CustomGroup

admin.site.unregister(Group)


@admin.register(CustomGroup)
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    filter_horizontal = ['permissions']
