<script lang="ts">
  import { onMount } from 'svelte';
  import DealCard from '../lib/components/DealCard.svelte';
  import ErrorBanner from '../lib/components/ErrorBanner.svelte';
  import { apiFetch } from '$lib/api';

  type Deal = {
    // Offer fields
    id: number;
    product_id: number;
    region: string;
    sale_type: 'dollar' | 'percent';
    discount_low: number;
    discount_high: number;
    currency: string;
    limit_qty: number | null;
    details: string | null;
    starts: string;
    ends: string;
    created_at: string;
    updated_at: string;
    // Product fields
    sku: string;
    name: string;
    category: string | null;
    brand: string | null;
    image_url: string | null;
    channel: string | null;
  };

  let deals: Deal[] = [];
  let loading = true;
  let error: string | null = null;

  onMount(async () => {
    try {
      // Get local date in YYYY-MM-DD (user's timezone)
      const now = new Date();
      const localDate =
        now.getFullYear() +
        '-' +
        String(now.getMonth() + 1).padStart(2, '0') +
        '-' +
        String(now.getDate()).padStart(2, '0');
      const res = await apiFetch(`/api/deals/today?date=${localDate}`);
      if (!res.ok) {
        if (res.status === 429) {
          throw new Error('Too many requests. Please wait a minute and refresh.');
        }
        throw new Error('We are having trouble loading deals right now. Please try again shortly.');
      }
      const json = await res.json();
      deals = json.data;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Unknown error';
    } finally {
      loading = false;
    }
  });
</script>

<main>
  <h1 style="font-size:2rem;font-weight:bold;margin-bottom:0.75rem;">Today's Deals</h1>
  <p style="margin-bottom:1.5rem;">
    <a
      href="https://www.costco.com/online-offers.html"
      target="_blank"
      rel="noopener noreferrer"
      style="color:#0070f3;text-decoration:underline;">See current online offers on Costco.com</a
    >
  </p>
  {#if loading}
    <p>Loading deals...</p>
  {:else if error}
    <ErrorBanner message={error} />
  {:else if deals.length === 0}
    <p>No deals found for today.</p>
  {:else}
    <div class="deals-grid">
      {#each deals as deal}
        <DealCard {...deal} />
      {/each}
    </div>
  {/if}
</main>

<style>
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    text-align: center;
  }
  .deals-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    justify-content: center;
    margin-top: 2rem;
  }
  @media (max-width: 700px) {
    .deals-grid {
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }
  }
</style>
