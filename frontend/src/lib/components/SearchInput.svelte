<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  let value = '';
  const dispatch = createEventDispatcher();

  function handleSubmit() {
    dispatch('search', value);
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <div class="join">
    <input class="input input-bordered join-item" placeholder="Search for products..." bind:value />
    <button class="btn join-item rounded-r-full">Search</button>
  </div>
</form>
