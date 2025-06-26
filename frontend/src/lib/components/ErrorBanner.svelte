<script lang="ts">
  export let message: string;
</script>

<div class="error-banner" role="alert">
  <span class="icon">⚠️</span>
  <span>{message}</span>
</div>

<style>
  .error-banner {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #fef2f2; /* red-50 */
    border: 1px solid #fecaca; /* red-200 */
    color: #b91c1c; /* red-700 */
    padding: 0.75rem 1rem;
    border-radius: 0.375rem;
    max-width: 600px;
    margin: 1rem auto;
    font-size: 0.95rem;
  }
  .icon {
    font-size: 1.2rem;
  }
</style>
