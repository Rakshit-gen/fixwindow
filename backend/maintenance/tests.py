from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .models import Category, MaintenanceRequest, Property, Unit, Vendor
from .serializers import MaintenanceRequestSerializer
from .services import compute_sla_statuses, compute_vendor_scorecards


class ComputeSlaStatusesTests(TestCase):
    def setUp(self):
        self.now = timezone.now()
        prop = Property.objects.create(name="Maple Duplex", address="1 Maple St")
        self.unit = Unit.objects.create(property=prop, label="Unit A")

    def test_resolved_requests_are_excluded(self):
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="Tam", category=Category.EMERGENCY,
            reported_at=self.now - timedelta(hours=10), resolved_at=self.now,
        )
        self.assertEqual(compute_sla_statuses(), [])

    def test_fresh_request_is_on_track(self):
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="Tam", category=Category.URGENT,
            reported_at=self.now - timedelta(hours=1),
        )
        self.assertEqual(compute_sla_statuses()[0].status, "on_track")

    def test_past_75_percent_of_sla_is_at_risk(self):
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="Tam", category=Category.EMERGENCY,
            reported_at=self.now - timedelta(hours=3.5),  # 4h SLA, 87.5% elapsed
        )
        self.assertEqual(compute_sla_statuses()[0].status, "at_risk")

    def test_past_sla_is_breached(self):
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="Tam", category=Category.EMERGENCY,
            reported_at=self.now - timedelta(hours=5),
        )
        self.assertEqual(compute_sla_statuses()[0].status, "breached")

    def test_breached_sorts_before_at_risk_and_on_track(self):
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="A", category=Category.ROUTINE,
            reported_at=self.now - timedelta(hours=1),
        )
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="B", category=Category.EMERGENCY,
            reported_at=self.now - timedelta(hours=5),
        )
        statuses = compute_sla_statuses()
        self.assertEqual(statuses[0].status, "breached")
        self.assertEqual(statuses[0].tenant_name, "B")


class ComputeVendorScorecardsTests(TestCase):
    def setUp(self):
        self.now = timezone.now()
        prop = Property.objects.create(name="Maple Duplex", address="1 Maple St")
        self.unit = Unit.objects.create(property=prop, label="Unit A")

    def test_vendor_with_no_resolved_requests_has_zero_stats(self):
        Vendor.objects.create(name="Slow Plumbing")
        card = compute_vendor_scorecards()[0]
        self.assertEqual(card.resolved_count, 0)
        self.assertIsNone(card.avg_resolution_hours)

    def test_breach_rate_reflects_sla_misses(self):
        vendor = Vendor.objects.create(name="Fast Fix")
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="A", category=Category.EMERGENCY, vendor=vendor,
            reported_at=self.now - timedelta(hours=10),
            acknowledged_at=self.now - timedelta(hours=9),
            resolved_at=self.now - timedelta(hours=8),  # 2h resolution, within 4h SLA
        )
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="B", category=Category.EMERGENCY, vendor=vendor,
            reported_at=self.now - timedelta(hours=20),
            acknowledged_at=self.now - timedelta(hours=19),
            resolved_at=self.now - timedelta(hours=10),  # 10h resolution, breached
        )
        card = compute_vendor_scorecards()[0]
        self.assertEqual(card.resolved_count, 2)
        self.assertEqual(card.breach_rate, 50.0)

    def test_scorecards_sorted_by_breach_rate_ascending(self):
        good = Vendor.objects.create(name="Reliable Rae")
        bad = Vendor.objects.create(name="Late Larry")
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="A", category=Category.URGENT, vendor=good,
            reported_at=self.now - timedelta(hours=30),
            resolved_at=self.now - timedelta(hours=20),  # within 24h SLA
        )
        MaintenanceRequest.objects.create(
            unit=self.unit, tenant_name="B", category=Category.URGENT, vendor=bad,
            reported_at=self.now - timedelta(hours=60),
            resolved_at=self.now - timedelta(hours=10),  # 50h resolution, breached
        )
        cards = compute_vendor_scorecards()
        self.assertEqual(cards[0].vendor_name, "Reliable Rae")


class MaintenanceRequestSerializerTests(TestCase):
    def setUp(self):
        self.now = timezone.now()
        prop = Property.objects.create(name="Maple Duplex", address="1 Maple St")
        self.unit = Unit.objects.create(property=prop, label="Unit A")

    def test_resolved_at_before_reported_at_is_rejected(self):
        serializer = MaintenanceRequestSerializer(data={
            "unit": self.unit.id, "tenant_name": "Tam", "category": Category.ROUTINE,
            "description": "leaky faucet",
            "reported_at": self.now.isoformat(),
            "resolved_at": (self.now - timedelta(hours=1)).isoformat(),
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_resolved_at_after_reported_at_is_accepted(self):
        serializer = MaintenanceRequestSerializer(data={
            "unit": self.unit.id, "tenant_name": "Tam", "category": Category.ROUTINE,
            "description": "leaky faucet",
            "reported_at": self.now.isoformat(),
            "resolved_at": (self.now + timedelta(hours=1)).isoformat(),
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_acknowledged_at_before_reported_at_is_rejected(self):
        serializer = MaintenanceRequestSerializer(data={
            "unit": self.unit.id, "tenant_name": "Tam", "category": Category.ROUTINE,
            "description": "leaky faucet",
            "reported_at": self.now.isoformat(),
            "acknowledged_at": (self.now - timedelta(hours=1)).isoformat(),
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_resolved_at_before_acknowledged_at_is_rejected(self):
        serializer = MaintenanceRequestSerializer(data={
            "unit": self.unit.id, "tenant_name": "Tam", "category": Category.ROUTINE,
            "description": "leaky faucet",
            "reported_at": self.now.isoformat(),
            "acknowledged_at": (self.now + timedelta(hours=2)).isoformat(),
            "resolved_at": (self.now + timedelta(hours=1)).isoformat(),
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
