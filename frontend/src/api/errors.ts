export function formatApiError(err: unknown): string {
  if (err instanceof Error) return err.message;
  if (typeof err === 'string') return err;
  return 'Request failed';
}

export function parseDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === 'object' && 'msg' in item) {
          return String(item.msg);
        }
        return String(item);
      })
      .join('; ');
  }
  if (detail && typeof detail === 'object' && 'msg' in detail) {
    return String((detail as { msg: string }).msg);
  }
  return 'Request failed';
}
