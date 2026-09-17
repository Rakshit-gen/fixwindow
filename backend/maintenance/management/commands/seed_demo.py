from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from maintenance.models import Category, MaintenanceRequest, Property, Unit, Vendor


class Command(BaseCommand):
    help = "Seeds demo properties, units, vendors, and maintenance requests."

    def handle(self, *args, **options):
        now = timezone.now()

        maple = Property.objects.get_or_create(name="Maple Duplex", defaults={"address": "12 Maple St"})[0]
        unit_a = Unit.objects.get_or_create(property=maple, label="Unit A")[0]
        unit_b = Unit.objects.get_or_create(property=maple, label="Unit B")[0]

        fast = Vendor.objects.get_or_create(
            name="Fast Fix Plumbing", defaults={"trade": "Plumbing", "contact": "555-0101"}
        )[0]
        slow = Vendor.objects.get_or_create(
            name="Slowpoke Electric", defaults={"trade": "Electrical", "contact": "555-0102"}
        )[0]

        # Breached: emergency reported 6h ago, still open.
        MaintenanceRequest.objects.get_or_create(
            unit=unit_a, tenant_name="Tam Torres", category=Category.EMERGENCY,
            description="No heat", reported_at=now - timedelta(hours=6),
        )

        # At risk: urgent reported 20h ago (SLA 24h), still open.
        MaintenanceRequest.objects.get_or_create(
            unit=unit_b, tenant_name="Sam Singh", category=Category.URGENT,
            description="Broken lock", reported_at=now - timedelta(hours=20),
        )

        # Resolved on time by a fast vendor.
        MaintenanceRequest.objects.get_or_create(
            unit=unit_a, tenant_name="Tam Torres", category=Category.URGENT,
            description="No hot water", vendor=fast,
            reported_at=now - timedelta(days=10),
            defaults={
                "acknowledged_at": now - timedelta(days=10) + timedelta(hours=1),
                "resolved_at": now - timedelta(days=10) + timedelta(hours=5),
            },
        )

        # Resolved late by a slow vendor.
        MaintenanceRequest.objects.get_or_create(
            unit=unit_b, tenant_name="Sam Singh", category=Category.URGENT,
            description="Flickering lights", vendor=slow,
            reported_at=now - timedelta(days=15),
            defaults={
                "acknowledged_at": now - timedelta(days=15) + timedelta(hours=10),
                "resolved_at": now - timedelta(days=15) + timedelta(hours=48),
            },
        )

        self.stdout.write(self.style.SUCCESS("Seeded demo properties, vendors, and requests."))
