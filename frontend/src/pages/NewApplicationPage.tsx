import { type FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { formatApiError } from '../api/errors';
import { useAuth } from '../auth/AuthContext';

const APPLICATION_TYPES = [
  'product_registration',
  'import_permit',
  'gmp_certificate',
  'variation_amendment',
];

export default function NewApplicationPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    application_type: 'product_registration',
    product_name: '',
    applicant_org: user?.organization || '',
    description: '',
  });

  const canCreate =
    user?.role === 'applicant' ||
    user?.role === 'admin' ||
    user?.role === 'technical_reviewer';

  if (!canCreate) {
    return (
      <div>
        <p className="error">Your role cannot create applications.</p>
        <Link to="/applications">Back to applications</Link>
      </div>
    );
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const created = await api.createApplication(form);
      navigate(`/applications/${created.id}`);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <p><Link to="/applications">← Back to applications</Link></p>
      <h1>Create regulatory application</h1>
      <p className="page-desc">
        Submit a new draft application. All data is synthetic for portfolio demo purposes.
      </p>

      <form className="card form-card" onSubmit={handleSubmit}>
        <label>
          Application type
          <select
            value={form.application_type}
            onChange={(e) => setForm({ ...form, application_type: e.target.value })}
          >
            {APPLICATION_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        </label>
        <label>
          Product name
          <input
            value={form.product_name}
            onChange={(e) => setForm({ ...form, product_name: e.target.value })}
            placeholder="e.g. Amoxicillin 500mg Capsules"
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
            placeholder="Brief description of the regulatory submission..."
            required
            rows={4}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <div className="action-buttons">
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create draft application'}
          </button>
          <Link to="/applications" className="btn-secondary" style={{ display: 'inline-block', padding: '0.5rem 1rem' }}>
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
