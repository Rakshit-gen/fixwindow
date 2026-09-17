from rest_framework import serializers

from .models import MaintenanceRequest, Property, Unit, Vendor


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ["id", "name", "address"]


class UnitSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source="property.name", read_only=True)

    class Meta:
        model = Unit
        fields = ["id", "property", "property_name", "label"]


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["id", "name", "trade", "contact"]


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    unit_label = serializers.CharField(source="unit.__str__", read_only=True)
    vendor_name = serializers.CharField(source="vendor.name", read_only=True, default=None)

    class Meta:
        model = MaintenanceRequest
        fields = [
            "id", "unit", "unit_label", "tenant_name", "category", "description",
            "vendor", "vendor_name", "reported_at", "acknowledged_at", "resolved_at",
        ]


class SlaStatusSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    unit = serializers.CharField()
    tenant_name = serializers.CharField()
    category = serializers.CharField()
    reported_at = serializers.DateTimeField()
    hours_elapsed = serializers.FloatField()
    sla_hours = serializers.FloatField()
    status = serializers.CharField()


class VendorScorecardSerializer(serializers.Serializer):
    vendor_name = serializers.CharField()
    resolved_count = serializers.IntegerField()
    avg_response_hours = serializers.FloatField(allow_null=True)
    avg_resolution_hours = serializers.FloatField(allow_null=True)
    breach_rate = serializers.FloatField()
