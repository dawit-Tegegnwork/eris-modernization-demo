import { type FormEvent, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { formatApiError } from '../api/errors';

export default function LoginPage() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState('applicant@demo.local');
  const [password, setPassword] = useState('Demo123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>eRIS Modernization Demo</h1>
        <p className="subtitle">Synthetic regulatory information system — portfolio reference only</p>
        <form onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
        <div className="demo-accounts">
          <p>Demo accounts (password: <code>Demo123!</code>)</p>
          <ul>
            <li><code>applicant@demo.local</code> — submit applications</li>
            <li><code>reviewer@demo.local</code> — technical review</li>
            <li><code>admin@demo.local</code> — full access</li>
            <li><code>auditor@demo.local</code> — audit log read-only</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
