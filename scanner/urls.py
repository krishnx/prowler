from django.urls import path, include
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from .views import ScanViewSet, CheckInfoViewSet, FindingViewSet

router = DefaultRouter()
router.register(r'scans', ScanViewSet, basename='scan')
router.register(r'checks', CheckInfoViewSet, basename='check')
router.register(r'findings', FindingViewSet, basename='finding')

schema_view = get_schema_view(
    openapi.Info(
        title='Prowler Scan API',
        default_version='v1',
        description='API documentation for Prowler Scan app',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/', include(router.urls)),
]
