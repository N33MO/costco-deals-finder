<script lang="ts">
  import { page } from '$app/stores';
  import { derived } from 'svelte/store';

  // Get the current path for active link highlighting
  const currentPath = derived(page, $page => $page.url.pathname);
</script>

<nav class="navbar">
  <div class="navbar-brand">
    <a href="/" class="app-title">Costco Deals Finder</a>
  </div>
  <ul class="navbar-links">
    <li><a href="/" class:active={$currentPath === '/'}>Today's Deals</a></li>
    <li>
      <a href="/history" class:active={$currentPath.startsWith('/history')}>Historical Deals</a>
    </li>
    <li><a href="/search" class:active={$currentPath.startsWith('/search')}>Search</a></li>
  </ul>
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
  .navbar-links {
    display: flex;
    gap: 2rem;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .navbar-links a {
    color: #374151;
    text-decoration: none;
    font-weight: 500;
    font-size: 1rem;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    transition: background 0.15s;
  }
  .navbar-links a.active,
  .navbar-links a:hover {
    background: #e0e7ef;
    color: #1a56db;
  }
  @media (max-width: 600px) {
    .navbar {
      flex-direction: column;
      align-items: flex-start;
      padding: 1rem;
    }
    .navbar-links {
      gap: 1rem;
      margin-top: 0.5rem;
    }
  }
</style>
