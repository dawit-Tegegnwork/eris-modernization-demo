import { type FormEvent, useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api, type Application } from '../api/client';
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
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    application_type: 'product_registration',
    product_name: '',
    applicant_org: user?.organization || '',
    description: '',
  });

  const statusFilter = searchParams.get('status') || '';
  const typeFilter = searchParams.get('type') || '';

  const load = () => {
    const params: { status?: string; application_type?: string } = {};
    if (statusFilter) params.status = statusFilter;
    if (typeFilter) params.application_type = typeFilter;
    api.applications(params).then(setApps).catch((e) => setError(e.message));
  };

  useEffect(() => {
    load();
  }, [statusFilter, typeFilter]);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.createApplication(form);
      setShowForm(false);
      setForm({ ...form, product_name: '', description: '' });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Create failed');
    }
  };

  const canCreate = user?.role === 'applicant' || user?.role === 'admin' || user?.role === 'technical_reviewer';

  return (
    <div>
      <div className="page-header">
        <h1>Regulatory Applications</h1>
        {canCreate && (
          <button type="button" className="btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : 'New Application'}
          </button>
        )}
      </div>

      {showForm && (
        <form className="card form-card" onSubmit={handleCreate}>
          <h2>Create Application</h2>
          <label>
            Type
            <select
              value={form.application_type}
              onChange={(e) => setForm({ ...form, application_type: e.target.value })}
            >
              {APPLICATION_TYPES.map((t) => (
                <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </label>
          <label>
            Product name
            <input
              value={form.product_name}
              onChange={(e) => setForm({ ...form, product_name: e.target.value })}
              required
            />
          </label>
          <label>
            Applicant organization
            <input
              value={form.applicant_org}
              onChange={(e) => setForm({ ...form, applicant_org: e.target.value })}
              required
            />
          </label>
          <label>
            Description
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              required
              rows={3}
            />
          </label>
          <button type="submit" className="btn-primary">Create draft</button>
        </form>
      )}

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
            <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
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
            <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
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
              <td><Link to={`/applications/${app.id}`}>{app.reference_number}</Link></td>
              <td>{app.product_name}</td>
              <td>{app.application_type.replace(/_/g, ' ')}</td>
              <td>{app.applicant_org}</td>
              <td><StatusBadge status={app.status} /></td>
              <td>{app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : '—'}</td>
            </tr>
          ))}
          {apps.length === 0 && (
            <tr><td colSpan={6}>No applications found.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
