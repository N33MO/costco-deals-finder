<script lang="ts">
  // import ToggleSwitch from './ToggleSwitch.svelte';
  // import { loadPictures } from '$lib/stores/settings';
  import { page } from '$app/stores';

  /**
   * Returns true if the current url pathname matches the target path.
   * For prefix routes like "/search", we use startsWith to cover sub-routes.
   */
  const isActive = (path: string) => {
    return $page.url.pathname === path || $page.url.pathname.startsWith(path + '/');
  };
</script>

<nav class="navbar">
  <div class="navbar-brand">
    <a href="/" class="app-title">Costco Deals Finder</a>
  </div>
  <div class="flex-none">
    <ul class="menu px-1">
      <li><a href="/" class="nav-button {isActive('/') ? 'active' : ''}">Today's Deals</a></li>
      <li>
        <a href="/search" class="nav-button {isActive('/search') ? 'active' : ''}">Search Deals</a>
      </li>
      <!--
      <li>
        <ToggleSwitch label="Load Images" bind:checked={$loadPictures} />
      </li>
      -->
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
    /* Center the brand title */
    .navbar-brand {
      width: 100%;
      text-align: center;
      margin-bottom: 1.2rem; /* increased gap */
    }
    .navbar-brand .app-title {
      display: inline-block;
    }
    /* Ensure buttons container aligns to the right */
    .navbar {
      align-items: stretch; /* allow children width 100% */
    }
    .flex-none {
      align-self: center; /* center horizontally */
      width: 100%;
    }
    .menu {
      justify-content: center; /* buttons centered */
      width: 100%;
    }
  }
  /* Navigation Menu Styles */
  .menu {
    list-style: none; /* Remove default list bullets */
    display: flex; /* Arrange items horizontally */
    gap: 1rem; /* Space between items */
    padding: 0;
    margin: 0;
  }

  .nav-button {
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    background: #e2e8f0;
    color: #1a202c;
    text-decoration: none;
    font-weight: 500;
    transition: background 0.2s ease;
    white-space: nowrap; /* prevent unwanted text wrap */
  }

  .nav-button:hover,
  .nav-button:focus {
    background: #cbd5e1;
  }

  /* Active link */
  .nav-button.active {
    background: #1a202c;
    color: #ffffff;
  }
</style>
