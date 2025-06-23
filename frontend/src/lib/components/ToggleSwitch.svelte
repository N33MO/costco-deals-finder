<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let checked = false;
  export let label = '';

  const dispatch = createEventDispatcher();

  function handleChange(event: Event) {
    const target = event.target as HTMLInputElement;
    checked = target.checked;
    dispatch('change', checked);
  }
</script>

<div class="form-control">
  <label class="label cursor-pointer">
    <span class="label-text">{label}</span>
    <input type="checkbox" class="toggle" bind:checked on:change={handleChange} />
  </label>
</div>
