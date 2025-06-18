<script lang="ts">
  export let sku: string;
  export let name: string;
  export let category: string | null = null;
  export let brand: string | null = null;
  export let region: string;
  export let sale_type: 'dollar' | 'percent';
  export let discount_low: number;
  export let discount_high: number;
  export let currency: string;
  export let limit_qty: number | null = null;
  export let details: string | null = null;
  export let starts: string;
  export let ends: string;
</script>

<div class="deal-card">
  <div class="deal-header">
    <h2>{name}</h2>
    <span class="sku">SKU: {sku}</span>
  </div>
  <div class="deal-meta">
    <span>{category ?? '—'}</span>
    <span>{brand ?? '—'}</span>
    <span>{region}</span>
  </div>
  <div class="deal-discount">
    <span class="discount">
      {sale_type === 'dollar' ? currency + ' ' : ''}{discount_low}
      {#if discount_high !== discount_low}
        –{sale_type === 'dollar' ? currency + ' ' : ''}{discount_high}
      {/if}
      {sale_type === 'percent' ? '%' : ''} OFF
    </span>
    {#if limit_qty}
      <span class="limit">Limit: {limit_qty}</span>
    {/if}
  </div>
  <div class="deal-dates">
    <span>Valid: {starts} – {ends}</span>
  </div>
  {#if details}
    <div class="deal-details">{details}</div>
  {/if}
</div>

<style>
  .deal-card {
    background: #fff;
    border-radius: 0.75rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
    padding: 1.25rem 1.5rem;
    margin: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 220px;
    max-width: 340px;
    width: 100%;
  }
  .deal-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.5rem;
  }
  .deal-header h2 {
    font-size: 1.15rem;
    font-weight: 600;
    margin: 0;
  }
  .sku {
    font-size: 0.85rem;
    color: #888;
  }
  .deal-meta {
    display: flex;
    gap: 0.75rem;
    font-size: 0.93rem;
    color: #666;
  }
  .deal-discount {
    font-size: 1.1rem;
    font-weight: 500;
    color: #1a7f37;
    display: flex;
    gap: 1.5rem;
    align-items: center;
  }
  .discount {
    font-size: 1.2rem;
    font-weight: 700;
  }
  .limit {
    background: #f5f5f5;
    border-radius: 0.5rem;
    padding: 0.1rem 0.5rem;
    font-size: 0.95rem;
    color: #555;
  }
  .deal-dates {
    font-size: 0.95rem;
    color: #444;
  }
  .deal-details {
    font-size: 0.95rem;
    color: #333;
    background: #f8f8f8;
    border-radius: 0.5rem;
    padding: 0.5rem 0.75rem;
  }
</style>
