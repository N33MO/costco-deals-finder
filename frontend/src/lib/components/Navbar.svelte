<script lang="ts">
  import ToggleSwitch from './ToggleSwitch.svelte';
  import { loadPictures } from '$lib/stores/settings';
</script>

<nav class="navbar">
  <div class="navbar-brand">
    <a href="/" class="app-title">Costco Deals Finder</a>
  </div>
  <div class="flex-1">
    <a href="/" class="btn btn-ghost normal-case text-xl">Costco Deals</a>
  </div>
  <div class="flex-none">
    <ul class="menu menu-horizontal px-1">
      <li><a href="/">Today's Deals</a></li>
      <li><a href="/search">Search</a></li>
      <li>
        <ToggleSwitch label="Load Images" bind:checked={$loadPictures} />
      </li>
    </ul>
  </div>
</nav>

<style>
  .navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    background: #f8fafc;
    border-bottom: 1px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  .navbar-brand .app-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a202c;
    text-decoration: none;
    letter-spacing: 0.01em;
  }
  @media (max-width: 600px) {
    .navbar {
      flex-direction: column;
      align-items: flex-start;
      padding: 1rem;
    }
  }
</style>
