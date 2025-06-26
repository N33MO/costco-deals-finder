<script lang="ts">
  export let year: number = new Date().getFullYear();
</script>

<footer class="footer">
  <small>
    Costco Deals Finder © {year} N33MO C. —
    <a href="/LICENSE" class="license-link">MIT License</a>&nbsp;|&nbsp;
    <a
      href="https://github.com/N33MO/costco-deals-finder"
      class="github-link"
      target="_blank"
      rel="noopener">GitHub – bugs</a
    ><br />
    Unofficial project — not affiliated with or endorsed by Costco Wholesale Corp.
  </small>
</footer>

<style>
  .footer {
    padding: 2rem 1rem;
    text-align: center;
    font-size: 0.875rem;
    color: #666;
    border-top: 1px solid #e5e5e5;
    margin-top: 3rem;
  }
  .disclaimer {
    margin-top: 0.5rem;
    font-style: italic;
    color: #999;
  }
</style>
