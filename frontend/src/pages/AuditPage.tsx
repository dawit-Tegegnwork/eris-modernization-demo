import { useEffect, useState } from 'react';
import { api, type AuditEvent } from '../api/client';

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    api.audit().then(setEvents).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!events.length && !error) return <div className="loading">Loading audit log...</div>;

  return (
    <div>
      <h1>Audit Log</h1>
      <p className="page-desc">Append-only audit trail — synthetic demo data only.</p>
      <table className="data-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Action</th>
            <th>Actor</th>
            <th>Entity</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e) => (
            <tr key={e.id}>
              <td>{new Date(e.created_at).toLocaleString()}</td>
              <td><code>{e.action}</code></td>
              <td>{e.actor_id?.slice(0, 8) || '—'}...</td>
              <td>{e.entity_type} / {e.entity_id?.slice(0, 8)}...</td>
              <td><code>{JSON.stringify(e.metadata_json).slice(0, 80)}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
