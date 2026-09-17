import csv

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MaintenanceRequest, Property, Unit, Vendor
from .serializers import (
    MaintenanceRequestSerializer,
    PropertySerializer,
    SlaStatusSerializer,
    UnitSerializer,
    VendorScorecardSerializer,
    VendorSerializer,
)
from .services import compute_sla_statuses, compute_vendor_scorecards


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by("name")
    serializer_class = PropertySerializer


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related("property").all()
    serializer_class = UnitSerializer


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all().order_by("name")
    serializer_class = VendorSerializer


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.select_related("unit", "vendor").all()
    serializer_class = MaintenanceRequestSerializer


class SlaStatusView(APIView):
    def get(self, request):
        return Response(SlaStatusSerializer(compute_sla_statuses(), many=True).data)


class VendorScorecardView(APIView):
    def get(self, request):
        return Response(VendorScorecardSerializer(compute_vendor_scorecards(), many=True).data)


class VendorScorecardCsvView(APIView):
    """Downloadable copy of the vendor scorecards, for pasting into a lease renewal review."""

    def get(self, request):
        cards = compute_vendor_scorecards()

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="fixwindow_vendor_scorecards.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ["vendor_name", "resolved_count", "avg_response_hours", "avg_resolution_hours", "breach_rate"]
        )
        for c in cards:
            writer.writerow(
                [c.vendor_name, c.resolved_count, c.avg_response_hours, c.avg_resolution_hours, c.breach_rate]
            )
        return response
