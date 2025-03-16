from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RolesViewSet, PermissionViewSet

router = DefaultRouter()
router.register(r'roles', RolesViewSet)
router.register(r'permissions', PermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
