import { describe, it, expect } from 'vitest';
import worker from '../../src/index';

describe('Worker', () => {
  it('should return 200 for root path', async () => {
    const request = new Request('http://localhost/');
    const response = await worker.fetch(request);
    expect(response.status).toBe(200);
    expect(await response.text()).toBe('Costco Deals Finder API');
  });

  it('should return 404 for unknown paths', async () => {
    const request = new Request('http://localhost/unknown');
    const response = await worker.fetch(request);
    expect(response.status).toBe(404);
  });
});
