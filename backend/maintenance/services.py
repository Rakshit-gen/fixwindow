from dataclasses import dataclass

from django.utils import timezone

from .models import MaintenanceRequest, SLA_HOURS, Vendor

AT_RISK_RATIO = 0.75


@dataclass
class SlaStatus:
    request_id: int
    unit: str
    tenant_name: str
    category: str
    reported_at: object
    hours_elapsed: float
    sla_hours: float
    status: str  # "on_track", "at_risk", "breached"


def compute_sla_statuses() -> list[SlaStatus]:
    """Every open (unresolved) request's SLA clock, worst-first."""
    now = timezone.now()
    statuses = []

    for req in MaintenanceRequest.objects.filter(resolved_at__isnull=True).select_related(
        "unit", "unit__property"
    ):
        sla_hours = SLA_HOURS[req.category]
        hours_elapsed = (now - req.reported_at).total_seconds() / 3600

        if hours_elapsed >= sla_hours:
            status = "breached"
        elif hours_elapsed >= sla_hours * AT_RISK_RATIO:
            status = "at_risk"
        else:
            status = "on_track"

        statuses.append(
            SlaStatus(
                request_id=req.id,
                unit=str(req.unit),
                tenant_name=req.tenant_name,
                category=req.category,
                reported_at=req.reported_at,
                hours_elapsed=round(hours_elapsed, 1),
                sla_hours=sla_hours,
                status=status,
            )
        )

    order = {"breached": 0, "at_risk": 1, "on_track": 2}
    statuses.sort(key=lambda s: (order[s.status], -s.hours_elapsed))
    return statuses


@dataclass
class VendorScorecard:
    vendor_name: str
    resolved_count: int
    avg_response_hours: float | None
    avg_resolution_hours: float | None
    breach_rate: float


def compute_vendor_scorecards() -> list[VendorScorecard]:
    """Response/resolution/breach-rate stats per vendor, across resolved requests."""
    scorecards = []

    for vendor in Vendor.objects.all():
        resolved = list(vendor.requests.filter(resolved_at__isnull=False))
        if not resolved:
            scorecards.append(
                VendorScorecard(vendor.name, 0, None, None, 0.0)
            )
            continue

        response_hours = [
            (r.acknowledged_at - r.reported_at).total_seconds() / 3600
            for r in resolved
            if r.acknowledged_at
        ]
        resolution_hours = [(r.resolved_at - r.reported_at).total_seconds() / 3600 for r in resolved]
        breaches = sum(1 for r, hrs in zip(resolved, resolution_hours) if hrs > SLA_HOURS[r.category])

        scorecards.append(
            VendorScorecard(
                vendor_name=vendor.name,
                resolved_count=len(resolved),
                avg_response_hours=round(sum(response_hours) / len(response_hours), 1)
                if response_hours
                else None,
                avg_resolution_hours=round(sum(resolution_hours) / len(resolution_hours), 1),
                breach_rate=round(breaches / len(resolved) * 100, 1),
            )
        )

    scorecards.sort(key=lambda s: s.breach_rate)
    return scorecards
