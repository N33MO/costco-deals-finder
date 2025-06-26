<script lang="ts">
  import '../app.css';
  import Navbar from '../lib/components/Navbar.svelte';
  import Footer from '../lib/components/Footer.svelte';
</script>

<svelte:head>
  <meta name="google-site-verification" content="9IdFmGHtfzYjrDxcDq4w-5Rdlw4p4IvwNvKpS3a06VQ" />
</svelte:head>

<Navbar />
<slot />
<Footer />
