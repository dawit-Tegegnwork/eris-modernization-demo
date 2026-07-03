import { parseDetail } from './errors';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8010';

export type Role = 'applicant' | 'technical_reviewer' | 'admin' | 'auditor';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  organization: string;
}

export interface Application {
  id: string;
  reference_number: string;
  application_type: string;
  product_name: string;
  applicant_org: string;
  description: string;
  status: string;
  applicant_id: string;
  assigned_reviewer_id: string | null;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationDetail extends Application {
  checklist: {
    id: string;
    doc_type: string;
    label: string;
    required: boolean;
    received: boolean;
    notes: string;
  }[];
  history: {
    id: string;
    from_status: string | null;
    to_status: string;
    actor_id: string;
    note: string;
    created_at: string;
  }[];
  comments: {
    id: string;
    author_id: string;
    body: string;
    created_at: string;
  }[];
}

export interface DashboardSummary {
  counts_by_status: Record<string, number>;
  viewer_role: string;
  pending_review: number;
}

export interface AuditEvent {
  id: string;
  action: string;
  actor_id: string | null;
  entity_type: string;
  entity_id: string | null;
  synthetic_only: boolean;
  metadata_json: Record<string, unknown>;
  created_at: string;
}

function getToken(): string | null {
  return sessionStorage.getItem('eris_token');
}

export function setToken(token: string): void {
  sessionStorage.setItem('eris_token', token);
}

export function clearToken(): void {
  sessionStorage.removeItem('eris_token');
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(parseDetail(body.detail) || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string; role: Role; full_name: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<UserProfile>('/api/v1/auth/me'),
  dashboard: () => request<DashboardSummary>('/api/v1/dashboard/summary'),
  applications: (params?: { status?: string; application_type?: string }) => {
    const query = new URLSearchParams();
    if (params?.status) query.set('status', params.status);
    if (params?.application_type) query.set('application_type', params.application_type);
    const qs = query.toString();
    return request<Application[]>(`/api/v1/applications${qs ? `?${qs}` : ''}`);
  },
  application: (id: string) => request<ApplicationDetail>(`/api/v1/applications/${id}`),
  createApplication: (data: {
    application_type: string;
    product_name: string;
    applicant_org: string;
    description: string;
  }) =>
    request<Application>('/api/v1/applications', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  transition: (id: string, action: string, note = '') =>
    request<Application>(`/api/v1/applications/${id}/transition`, {
      method: 'POST',
      body: JSON.stringify({ action, note }),
    }),
  comment: (id: string, body: string) =>
    request(`/api/v1/applications/${id}/comments`, {
      method: 'POST',
      body: JSON.stringify({ body }),
    }),
  updateChecklist: (appId: string, itemId: string, received: boolean, notes = '') =>
    request(`/api/v1/applications/${appId}/checklist/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify({ received, notes }),
    }),
  audit: (limit = 100) => request<AuditEvent[]>(`/api/v1/audit?limit=${limit}`),
};
