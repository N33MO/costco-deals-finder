<script lang="ts">
  import SearchInput from '$lib/components/SearchInput.svelte';
  import DealHistoryCard from '$lib/components/DealHistoryCard.svelte';
  import ErrorBanner from '$lib/components/ErrorBanner.svelte';
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
  let loading = false;
  let error: string | null = null;
  let query = '';

  // Group deals by SKU
  $: groupedDeals = deals.reduce(
    (acc, deal) => {
      if (!acc[deal.sku]) {
        acc[deal.sku] = {
          name: deal.name,
          sku: deal.sku,
          image_url: deal.image_url,
          deals: [],
        };
      }
      acc[deal.sku].deals.push({
        starts: deal.starts,
        ends: deal.ends,
        discount:
          deal.sale_type === 'dollar'
            ? `${deal.currency} ${deal.discount_low}` +
              (deal.discount_high !== deal.discount_low
                ? `–${deal.currency} ${deal.discount_high}`
                : '')
            : `${deal.discount_low}` +
              (deal.discount_high !== deal.discount_low ? `–${deal.discount_high}` : '') +
              '%',
        sale_type: deal.sale_type,
        channel: deal.channel,
        limit_qty: deal.limit_qty,
        details: deal.details,
      });
      return acc;
    },
    {} as Record<
      string,
      {
        name: string;
        sku: string;
        image_url: string | null;
        deals: Array<{
          starts: string;
          ends: string;
          discount: string;
          sale_type: 'dollar' | 'percent';
          channel: string | null;
          limit_qty: number | null;
          details: string | null;
        }>;
      }
    >
  );

  async function handleSearch(event: CustomEvent<string>) {
    query = event.detail;
    if (!query) {
      deals = [];
      return;
    }
    loading = true;
    error = null;
    try {
      const res = await apiFetch(`/api/deals/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) {
        if (res.status === 429) {
          throw new Error('You are searching too quickly. Please wait a minute and try again.');
        }
        throw new Error('We are having trouble fetching search results. Please try again later.');
      }
      const json = await res.json();
      deals = json.data;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Unknown error';
    } finally {
      loading = false;
    }
  }
</script>

<main>
  <h1 style="font-size:2rem;font-weight:bold;margin-bottom:1.5rem;">Search Deals</h1>
  <SearchInput on:search={handleSearch} />

  <div class="results mt-8">
    {#if loading}
      <p>Loading results...</p>
    {:else if error}
      <ErrorBanner message={error} />
    {:else if deals.length === 0 && query}
      <p>No deals found for "{query}".</p>
    {:else if deals.length > 0}
      <div class="history-list">
        {#each Object.values(groupedDeals) as product}
          <DealHistoryCard
            name={product.name}
            sku={product.sku}
            image_url={product.image_url}
            deals={product.deals}
          />
        {/each}
      </div>
    {/if}
  </div>
</main>

<style>
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    text-align: center;
  }
  .history-list {
    display: flex;
    flex-direction: column;
    gap: 2.5rem;
    align-items: center;
    margin-top: 2rem;
  }
  @media (max-width: 700px) {
    .history-list {
      gap: 1.2rem;
    }
  }
</style>
