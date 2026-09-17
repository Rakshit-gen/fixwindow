import { useCallback, useEffect, useState } from "react";
import {
  acknowledgeRequest,
  fetchSlaStatuses,
  fetchVendorScorecards,
  resolveRequest,
  vendorScorecardsExportUrl,
  type SlaStatus,
  type VendorScorecard,
} from "./api";
import { NewRequestForm } from "./NewRequestForm";

export default function App() {
  const [statuses, setStatuses] = useState<SlaStatus[]>([]);
  const [scorecards, setScorecards] = useState<VendorScorecard[]>([]);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    Promise.all([fetchSlaStatuses(), fetchVendorScorecards()])
      .then(([s, v]) => {
        setStatuses(s);
        setScorecards(v);
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  async function handleAcknowledge(requestId: number) {
    await acknowledgeRequest(requestId);
    reload();
  }

  async function handleResolve(requestId: number) {
    await resolveRequest(requestId);
    reload();
  }

  return (
    <div className="app">
      <header>
        <h1>fixwindow</h1>
        <p>SLA clocks for open maintenance requests, and vendor response history.</p>
      </header>

      {error && <p className="error">{error}</p>}

      <NewRequestForm onCreated={reload} />

      <section>
        <h2>Open requests</h2>
        {statuses.length === 0 ? (
          <p className="empty">No open requests. Everything's resolved.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Unit</th>
                <th>Tenant</th>
                <th>Category</th>
                <th>Elapsed / SLA (hrs)</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {statuses.map((s) => (
                <tr key={s.request_id} className={`status-${s.status}`}>
                  <td>{s.unit}</td>
                  <td>{s.tenant_name}</td>
                  <td>{s.category}</td>
                  <td>
                    {s.hours_elapsed} / {s.sla_hours}
                  </td>
                  <td>{s.status.replace("_", " ")}</td>
                  <td className="actions">
                    <button onClick={() => handleAcknowledge(s.request_id)}>Acknowledge</button>
                    <button onClick={() => handleResolve(s.request_id)}>Resolve</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section>
        <h2>Vendor scorecards</h2>
        <a className="export-link" href={vendorScorecardsExportUrl()}>
          Export CSV
        </a>
        {scorecards.length === 0 ? (
          <p className="empty">No vendors yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Vendor</th>
                <th>Resolved</th>
                <th>Avg response (hrs)</th>
                <th>Avg resolution (hrs)</th>
                <th>Breach rate</th>
              </tr>
            </thead>
            <tbody>
              {scorecards.map((c) => (
                <tr key={c.vendor_name}>
                  <td>{c.vendor_name}</td>
                  <td>{c.resolved_count}</td>
                  <td>{c.avg_response_hours ?? "—"}</td>
                  <td>{c.avg_resolution_hours ?? "—"}</td>
                  <td>{c.breach_rate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
