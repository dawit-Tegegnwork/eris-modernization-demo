import { describe, expect, it } from 'vitest';
import { parseDetail } from './errors';

describe('parseDetail', () => {
  it('returns string detail as-is', () => {
    expect(parseDetail('Invalid credentials')).toBe('Invalid credentials');
  });

  it('formats FastAPI validation error arrays', () => {
    expect(
      parseDetail([
        { type: 'uuid_parsing', loc: ['path', 'id'], msg: 'Input should be a valid UUID' },
      ])
    ).toBe('Input should be a valid UUID');
  });
});
