<script lang="ts">
  import SearchInput from '$lib/components/SearchInput.svelte';
  import DealCard from '$lib/components/DealCard.svelte';

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

  async function handleSearch(event: any) {
    query = event.detail;
    if (!query) {
      deals = [];
      return;
    }
    loading = true;
    error = null;
    try {
      const res = await fetch(`/api/deals/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error('Failed to fetch search results');
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
      <p style="color: red">{error}</p>
    {:else if deals.length === 0 && query}
      <p>No deals found for "{query}".</p>
    {:else if deals.length > 0}
      <div class="deals-grid">
        {#each deals as deal}
          <DealCard {...deal} />
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
