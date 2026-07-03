const STATUS_COLORS: Record<string, string> = {
  draft: 'status-draft',
  submitted: 'status-submitted',
  under_technical_review: 'status-review',
  clarification_requested: 'status-clarification',
  approved: 'status-approved',
  rejected: 'status-rejected',
};

export default function StatusBadge({ status }: { status: string }) {
  const cls = STATUS_COLORS[status] || 'status-default';
  return <span className={`status-badge ${cls}`}>{status.replace(/_/g, ' ')}</span>;
}
