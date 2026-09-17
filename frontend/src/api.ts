const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000/api";

export type SlaStatus = {
  request_id: number;
  unit: string;
  tenant_name: string;
  category: string;
  reported_at: string;
  hours_elapsed: number;
  sla_hours: number;
  status: "on_track" | "at_risk" | "breached";
};

export type VendorScorecard = {
  vendor_name: string;
  resolved_count: number;
  avg_response_hours: number | null;
  avg_resolution_hours: number | null;
  breach_rate: number;
};

export type Unit = {
  id: number;
  property_name: string;
  label: string;
};

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const fetchSlaStatuses = () => getJson<SlaStatus[]>("/sla-status/");
export const fetchVendorScorecards = () => getJson<VendorScorecard[]>("/vendor-scorecards/");
export const fetchUnits = () => getJson<{ results?: Unit[] } | Unit[]>("/units/").then(
  (data) => (Array.isArray(data) ? data : data.results ?? [])
);

export async function createRequest(payload: {
  unit: number;
  tenant_name: string;
  category: string;
  description: string;
  reported_at: string;
}): Promise<void> {
  const res = await fetch(`${API_BASE}/requests/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to create request: ${res.status}`);
}
