from django.db import models


class Category(models.TextChoices):
    EMERGENCY = "emergency", "Emergency (no heat, flooding, gas leak)"
    URGENT = "urgent", "Urgent (no hot water, broken lock, appliance failure)"
    ROUTINE = "routine", "Routine (cosmetic, non-urgent repair)"

# Hours to acknowledge-and-resolve before a request breaches its SLA.
SLA_HOURS = {
    Category.EMERGENCY: 4,
    Category.URGENT: 24,
    Category.ROUTINE: 120,  # 5 business days
}


class Property(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Unit(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="units")
    label = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.property.name} - {self.label}"


class Vendor(models.Model):
    name = models.CharField(max_length=200)
    trade = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class MaintenanceRequest(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="requests")
    tenant_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="requests")
    reported_at = models.DateTimeField()
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-reported_at"]

    def __str__(self):
        return f"{self.unit} - {self.category} ({self.reported_at:%Y-%m-%d})"
