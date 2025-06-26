<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  let value = '';
  const dispatch = createEventDispatcher();

  function handleSubmit() {
    dispatch('search', value);
  }
</script>

<form class="search-card" on:submit|preventDefault={handleSubmit}>
  <input
    class="search-input"
    placeholder="Search for products…"
    bind:value
    aria-label="Search for products"
  />
  <button class="search-btn" type="submit">Search</button>
</form>

<style>
  /* Card container to match DealHistoryCard look */
  .search-card {
    background: #fff;
    border-radius: 0.75rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
    padding: 1.25rem 1.5rem;
    margin: 0 auto;
    max-width: 950px;
    width: 100%;
    display: flex;
    gap: 1rem;
    align-items: center;
    justify-content: center;
  }

  .search-input {
    flex: 1 1 0;
    min-width: 0;
    padding: 0.75rem 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    font-size: 1.05rem;
  }

  .search-input:focus {
    outline: none;
    border-color: #3182ce;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.3);
  }

  .search-btn {
    padding: 0.75rem 1.25rem;
    border: none;
    border-radius: 0.5rem;
    background: #1a202c;
    color: #ffffff;
    font-size: 1.05rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s ease;
    flex-shrink: 0;
  }

  .search-btn:hover,
  .search-btn:focus {
    background: #2d3748;
  }

  @media (max-width: 600px) {
    .search-card {
      flex-direction: column;
      gap: 0.75rem;
    }
    .search-btn {
      width: 100%;
    }
    .search-input {
      width: 100%;
    }
  }
</style>
