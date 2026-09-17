import { useEffect, useState } from "react";
import { createRequest, fetchUnits, type Unit } from "./api";

type Props = {
  onCreated: () => void;
};

export function NewRequestForm({ onCreated }: Props) {
  const [units, setUnits] = useState<Unit[]>([]);
  const [unitId, setUnitId] = useState<number | "">("");
  const [tenantName, setTenantName] = useState("");
  const [category, setCategory] = useState("routine");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUnits().then((u) => {
      setUnits(u);
      if (u.length > 0) setUnitId(u[0].id);
    });
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!unitId) return;
    try {
      await createRequest({
        unit: unitId,
        tenant_name: tenantName,
        category,
        description,
        reported_at: new Date().toISOString(),
      });
      setTenantName("");
      setDescription("");
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to log request");
    }
  }

  return (
    <form className="new-request" onSubmit={handleSubmit}>
      <h2>Log a maintenance request</h2>
      {error && <p className="error">{error}</p>}
      <div className="form-row">
        <select value={unitId} onChange={(e) => setUnitId(Number(e.target.value))} required>
          {units.map((u) => (
            <option key={u.id} value={u.id}>
              {u.property_name} - {u.label}
            </option>
          ))}
        </select>
        <input
          placeholder="Tenant name"
          value={tenantName}
          onChange={(e) => setTenantName(e.target.value)}
          required
        />
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="emergency">Emergency (4h SLA)</option>
          <option value="urgent">Urgent (24h SLA)</option>
          <option value="routine">Routine (5 day SLA)</option>
        </select>
      </div>
      <textarea
        placeholder="What's wrong?"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <button type="submit">Log request</button>
    </form>
  );
}
