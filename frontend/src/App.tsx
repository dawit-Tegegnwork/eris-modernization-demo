import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import ApplicationDetailPage from './pages/ApplicationDetailPage';
import ApplicationsPage from './pages/ApplicationsPage';
import AuditPage from './pages/AuditPage';
import DashboardPage from './pages/DashboardPage';
import LoginPage from './pages/LoginPage';
import NewApplicationPage from './pages/NewApplicationPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="applications" element={<ApplicationsPage />} />
            <Route path="applications/new" element={<NewApplicationPage />} />
            <Route path="applications/:id" element={<ApplicationDetailPage />} />
            <Route
              path="audit"
              element={
                <ProtectedRoute roles={['admin', 'auditor']}>
                  <AuditPage />
                </ProtectedRoute>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
