from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    MaintenanceRequestViewSet,
    PropertyViewSet,
    SlaStatusView,
    UnitViewSet,
    VendorScorecardView,
    VendorViewSet,
)

router = DefaultRouter()
router.register("properties", PropertyViewSet)
router.register("units", UnitViewSet)
router.register("vendors", VendorViewSet)
router.register("requests", MaintenanceRequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("sla-status/", SlaStatusView.as_view()),
    path("vendor-scorecards/", VendorScorecardView.as_view()),
]
