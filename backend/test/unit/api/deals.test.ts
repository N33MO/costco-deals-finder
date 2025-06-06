import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createTestContext } from '../../helpers/context';
import app from '../../../src/api/router';
import { Database } from '../../../src/db';
import type { OfferPeriod } from '../../../src/types/schema';

describe('Deals API', () => {
  let ctx: Awaited<ReturnType<typeof createTestContext>>;
  let mockGetCurrentOffers: ReturnType<typeof vi.fn<[string?], Promise<OfferPeriod[]>>>;

  beforeEach(async () => {
    ctx = await createTestContext();
    mockGetCurrentOffers = vi.fn();
    vi.spyOn(Database.prototype, 'getCurrentOffers').mockImplementation(
      async (region?: string): Promise<OfferPeriod[]> => {
        return mockGetCurrentOffers(region);
      }
    );
  });

  describe('GET /api/deals/today', () => {
    it('should return offers with metadata', async () => {
      const mockOffers: OfferPeriod[] = [
        {
          id: 1,
          product_id: 1,
          region: 'US',
          sale_type: 'dollar',
          discount_low: 5.0,
          discount_high: 5.0,
          currency: 'USD',
          limit_qty: 2,
          details: 'Test details',
          starts: '2024-03-20',
          ends: '2024-04-03',
          created_at: '2024-03-20T00:00:00Z',
          updated_at: '2024-03-20T00:00:00Z',
        },
      ];

      mockGetCurrentOffers.mockResolvedValue(mockOffers);

      const response = await app.fetch(new Request('http://localhost/api/deals/today'), ctx.env);
      expect(response.status).toBe(200);

      const data = await response.json();
      expect(data).toEqual({
        data: mockOffers,
        meta: {
          count: 1,
          region: 'US',
          timestamp: expect.any(String),
        },
      });
    });

    it('should return 500 when database query fails', async () => {
      mockGetCurrentOffers.mockRejectedValue(new Error('Database error'));

      const response = await app.fetch(new Request('http://localhost/api/deals/today'), ctx.env);
      expect(response.status).toBe(500);

      const data = await response.json();
      expect(data).toEqual({
        error: {
          message: 'Failed to fetch current deals: Database error',
          status: 500,
        },
      });
    });
  });
});
