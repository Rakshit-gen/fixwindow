from django.contrib import admin

from .models import MaintenanceRequest, Property, Unit, Vendor


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "address")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("property", "label")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "trade", "contact")


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ("unit", "category", "vendor", "reported_at", "resolved_at")
    list_filter = ("category",)
