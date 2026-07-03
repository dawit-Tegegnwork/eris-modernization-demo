import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, type ApplicationDetail } from '../api/client';
import { formatApiError } from '../api/errors';
import { useAuth } from '../auth/AuthContext';
import StatusBadge from '../components/StatusBadge';

const REVIEWER_ACTIONS: Record<string, { action: string; label: string; className?: string }[]> = {
  submitted: [{ action: 'pickup', label: 'Pick up for review' }],
  under_technical_review: [
    { action: 'request_clarification', label: 'Request clarification' },
    { action: 'approve', label: 'Approve', className: 'btn-success' },
    { action: 'reject', label: 'Reject', className: 'btn-danger' },
  ],
  clarification_requested: [],
};

export default function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [app, setApp] = useState<ApplicationDetail | null>(null);
  const [error, setError] = useState('');
  const [note, setNote] = useState('');
  const [comment, setComment] = useState('');

  const load = () => {
    if (!id) return;
    api.application(id).then(setApp).catch((e) => setError(formatApiError(e)));
  };

  useEffect(() => {
    load();
  }, [id]);

  const handleTransition = async (action: string) => {
    if (!id) return;
    try {
      await api.transition(id, action, note);
      setNote('');
      load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const handleComment = async () => {
    if (!id || !comment.trim()) return;
    try {
      await api.comment(id, comment);
      setComment('');
      load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  const handleChecklist = async (itemId: string, received: boolean) => {
    if (!id) return;
    try {
      await api.updateChecklist(id, itemId, received);
      load();
    } catch (err) {
      setError(formatApiError(err));
    }
  };

  if (error && !app) return <p className="error">{error}</p>;
  if (!app) return <div className="loading">Loading application...</div>;

  const isApplicant = user?.role === 'applicant' && app.applicant_id === user.id;
  const isReviewer = user?.role === 'technical_reviewer' || user?.role === 'admin';
  const canReview = isReviewer && (
    app.status === 'submitted' ||
    (app.status === 'under_technical_review' && (user?.role === 'admin' || app.assigned_reviewer_id === user?.id))
  );

  const applicantActions: { action: string; label: string; className?: string }[] =
    app.status === 'draft' && (isApplicant || user?.role === 'admin')
      ? [{ action: 'submit', label: 'Submit for review' }]
      : app.status === 'clarification_requested' && (isApplicant || user?.role === 'admin')
        ? [{ action: 'resubmit', label: 'Resubmit after clarification' }]
        : [];

  const reviewerActions = canReview ? (REVIEWER_ACTIONS[app.status] || []) : [];
  const actions = [...applicantActions, ...reviewerActions];

  return (
    <div>
      <p><Link to="/applications">← Back to applications</Link></p>
      <div className="page-header">
        <div>
          <h1>{app.reference_number}</h1>
          <p className="page-desc">{app.product_name} — {app.applicant_org}</p>
        </div>
        <StatusBadge status={app.status} />
      </div>

      {error && <p className="error">{error}</p>}

      <div className="detail-grid">
        <section className="card">
          <h2>Application details</h2>
          <dl className="detail-list">
            <dt>Type</dt><dd>{app.application_type.replace(/_/g, ' ')}</dd>
            <dt>Description</dt><dd>{app.description}</dd>
            <dt>Created</dt><dd>{new Date(app.created_at).toLocaleString()}</dd>
            <dt>Submitted</dt><dd>{app.submitted_at ? new Date(app.submitted_at).toLocaleString() : 'Not submitted'}</dd>
            <dt>Assigned reviewer</dt><dd>{app.assigned_reviewer_id || 'Unassigned'}</dd>
          </dl>
        </section>

        <section className="card">
          <h2>Document checklist</h2>
          <table className="data-table compact">
            <thead>
              <tr><th>Document</th><th>Required</th><th>Received</th></tr>
            </thead>
            <tbody>
              {app.checklist.map((item) => (
                <tr key={item.id}>
                  <td>{item.label}</td>
                  <td>{item.required ? 'Yes' : 'No'}</td>
                  <td>
                    {isReviewer ? (
                      <input
                        type="checkbox"
                        checked={item.received}
                        onChange={(e) => handleChecklist(item.id, e.target.checked)}
                      />
                    ) : (
                      item.received ? '✓' : '—'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>

      {actions.length > 0 && (
        <section className="card action-panel">
          <h2>Workflow actions</h2>
          <textarea
            placeholder="Optional note for this action..."
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={2}
          />
          <div className="action-buttons">
            {actions.map((a) => (
              <button
                key={a.action}
                type="button"
                className={a.className || 'btn-primary'}
                onClick={() => handleTransition(a.action)}
              >
                {a.label}
              </button>
            ))}
          </div>
        </section>
      )}

      <section className="card">
        <h2>Status history</h2>
        <ol className="timeline">
          {app.history.map((h) => (
            <li key={h.id}>
              <strong>{h.to_status.replace(/_/g, ' ')}</strong>
              {h.from_status && <span> (from {h.from_status.replace(/_/g, ' ')})</span>}
              <p>{h.note || '—'}</p>
              <time>{new Date(h.created_at).toLocaleString()}</time>
            </li>
          ))}
        </ol>
      </section>

      <section className="card">
        <h2>Comments</h2>
        <ul className="comment-list">
          {app.comments.map((c) => (
            <li key={c.id}>
              <p>{c.body}</p>
              <time>{new Date(c.created_at).toLocaleString()}</time>
            </li>
          ))}
          {app.comments.length === 0 && <li>No comments yet.</li>}
        </ul>
        <div className="comment-form">
          <textarea
            placeholder="Add a comment..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={2}
          />
          <button type="button" className="btn-secondary" onClick={handleComment}>Add comment</button>
        </div>
      </section>
    </div>
  );
}
