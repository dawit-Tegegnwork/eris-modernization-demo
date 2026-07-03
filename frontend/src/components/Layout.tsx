import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="header-inner">
          <Link to="/" className="logo">
            eRIS Modernization Demo
          </Link>
          <nav>
            <Link to="/">Dashboard</Link>
            <Link to="/applications">Applications</Link>
            {(user?.role === 'admin' || user?.role === 'auditor') && (
              <Link to="/audit">Audit Log</Link>
            )}
          </nav>
          <div className="user-bar">
            <span className="role-badge">{user?.role?.replace('_', ' ')}</span>
            <span>{user?.full_name}</span>
            <button type="button" onClick={handleLogout} className="btn-secondary">
              Logout
            </button>
          </div>
        </div>
      </header>
      <div className="banner">
        <strong>Synthetic demo only.</strong> Portfolio reference implementation — not a government
        production system.
      </div>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
