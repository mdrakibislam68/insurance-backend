from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularJSONAPIView
from rest_framework import routers

from general_settings.viewsets import GeneralSettingsViewSets
from integrations.viewsets import IntegrationsViewSet
from processes.viewsets import ProcessViewSets, ScheduledJobViewSets
from roles.views import RolesViewSet, PermissionViewSet
from user_management.viewsets import AuthViewSets

router = routers.DefaultRouter()
router.register(r'auth', AuthViewSets, basename='Authentication')
router.register(r'general-settings', GeneralSettingsViewSets, basename='GeneralSettings')
router.register(r'manage-integrations', IntegrationsViewSet, basename='IntegrationsManagement')
router.register(r'process-settings', ProcessViewSets, basename='ProcessSettings')
router.register(r'scheduled-jobs', ScheduledJobViewSets, basename='ScheduledJobs')
router.register(r'roles-permissions/roles', RolesViewSet, basename='Roles')
router.register(r'roles-permissions/permissions', PermissionViewSet, basename='Permissions')

urlpatterns = [
    path('', include(router.urls)),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema.json', SpectacularJSONAPIView.as_view(), name='schema'),
    path('rest-auth/', include('rest_framework.urls')),
    # path('roles-permissions/', include('roles.urls')),
]
