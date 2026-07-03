import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api, type Application } from '../api/client';
import { formatApiError } from '../api/errors';
import { useAuth } from '../auth/AuthContext';
import StatusBadge from '../components/StatusBadge';

const APPLICATION_TYPES = [
  'product_registration',
  'import_permit',
  'gmp_certificate',
  'variation_amendment',
];

const STATUSES = [
  'draft',
  'submitted',
  'under_technical_review',
  'clarification_requested',
  'approved',
  'rejected',
];

export default function ApplicationsPage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [apps, setApps] = useState<Application[]>([]);
  const [error, setError] = useState('');

  const statusFilter = searchParams.get('status') || '';
  const typeFilter = searchParams.get('type') || '';

  const load = () => {
    const params: { status?: string; application_type?: string } = {};
    if (statusFilter) params.status = statusFilter;
    if (typeFilter) params.application_type = typeFilter;
    api
      .applications(params)
      .then(setApps)
      .catch((e) => setError(formatApiError(e)));
  };

  useEffect(() => {
    load();
  }, [statusFilter, typeFilter]);

  const canCreate =
    user?.role === 'applicant' ||
    user?.role === 'admin' ||
    user?.role === 'technical_reviewer';

  return (
    <div>
      <div className="page-header">
        <h1>Regulatory Applications</h1>
        {canCreate && (
          <Link to="/applications/new" className="btn-primary" style={{ textDecoration: 'none' }}>
            New Application
          </Link>
        )}
      </div>

      <div className="filters">
        <select
          value={statusFilter}
          onChange={(e) => {
            const p = new URLSearchParams(searchParams);
            if (e.target.value) p.set('status', e.target.value);
            else p.delete('status');
            setSearchParams(p);
          }}
        >
          <option value="">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={(e) => {
            const p = new URLSearchParams(searchParams);
            if (e.target.value) p.set('type', e.target.value);
            else p.delete('type');
            setSearchParams(p);
          }}
        >
          <option value="">All types</option>
          {APPLICATION_TYPES.map((t) => (
            <option key={t} value={t}>
              {t.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="error">{error}</p>}

      <table className="data-table">
        <thead>
          <tr>
            <th>Reference</th>
            <th>Product</th>
            <th>Type</th>
            <th>Organization</th>
            <th>Status</th>
            <th>Submitted</th>
          </tr>
        </thead>
        <tbody>
          {apps.map((app) => (
            <tr key={app.id}>
              <td>
                <Link to={`/applications/${app.id}`}>{app.reference_number}</Link>
              </td>
              <td>{app.product_name}</td>
              <td>{app.application_type.replace(/_/g, ' ')}</td>
              <td>{app.applicant_org}</td>
              <td>
                <StatusBadge status={app.status} />
              </td>
              <td>
                {app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : '—'}
              </td>
            </tr>
          ))}
          {apps.length === 0 && (
            <tr>
              <td colSpan={6}>No applications found.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
