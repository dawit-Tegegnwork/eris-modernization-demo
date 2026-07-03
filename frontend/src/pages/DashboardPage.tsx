import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, type DashboardSummary } from '../api/client';
import { formatApiError } from '../api/errors';
import { useAuth } from '../auth/AuthContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.dashboard().then(setSummary).catch((e) => setError(formatApiError(e)));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!summary) return <div className="loading">Loading dashboard...</div>;

  const counts = summary.counts_by_status;

  return (
    <div>
      <h1>Regulatory Dashboard</h1>
      <p className="page-desc">
        Welcome, {user?.full_name}. Role: <strong>{user?.role?.replace('_', ' ')}</strong>
      </p>

      {(user?.role === 'technical_reviewer' || user?.role === 'admin') &&
        summary.pending_review > 0 && (
          <div className="alert">
            {summary.pending_review} application(s) awaiting technical review pickup.{' '}
            <Link to="/applications?status=submitted">View queue</Link>
          </div>
        )}

      <div className="kpi-grid">
        {Object.entries(counts).map(([status, count]) => (
          <div key={status} className="kpi-card">
            <span className="kpi-label">{status.replace(/_/g, ' ')}</span>
            <strong className="kpi-value">{count}</strong>
          </div>
        ))}
      </div>

      <div className="quick-actions">
        <h2>Quick actions</h2>
        <ul>
          <li><Link to="/applications">View all applications</Link></li>
          {(user?.role === 'applicant' ||
            user?.role === 'admin' ||
            user?.role === 'technical_reviewer') && (
            <li><Link to="/applications/new">Create new application</Link></li>
          )}
          {(user?.role === 'admin' || user?.role === 'auditor') && (
            <li><Link to="/audit">View audit log</Link></li>
          )}
        </ul>
      </div>
    </div>
  );
}
