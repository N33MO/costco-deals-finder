<!--
  DealHistoryEntry interface for documentation:
  interface DealHistoryEntry {
    starts: string;
    ends: string;
    discount: string; // e.g. "$5" or "20%"
    sale_type: 'dollar' | 'percent';
    channel: string | null; // "Online", "In-Warehouse", "Both", etc.
    limit_qty: number | null;
    details: string | null;
  }
-->
<script lang="ts">
  import { loadPictures } from '$lib/stores/settings';
  import { onMount } from 'svelte';

  export let name: string;
  export let image_url: string | null = null;
  export let sku: string;
  export let deals: Array<{
    starts: string;
    ends: string;
    discount: string;
    sale_type: 'dollar' | 'percent';
    channel: string | null;
    limit_qty: number | null;
    details: string | null;
  }> = [];

  // Helper functions
  /**
   * Parse a date string of the form "YYYY-MM-DD" into a Date
   * at local midnight (so no UTC shift).
   */
  function parseLocalDate(dateStr: string): Date {
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day);
  }
  function getYear(date: string): number {
    return parseLocalDate(date).getFullYear();
  }
  function daysInMonth(year: number, month: number): number {
    return new Date(year, month + 1, 0).getDate();
  }

  // Group deals by year, most recent year first
  $: dealsByYear = deals.reduce(
    (acc, deal) => {
      const year = getYear(deal.starts);
      if (!acc[year]) acc[year] = [];
      acc[year].push(deal);
      return acc;
    },
    {} as Record<number, typeof deals>
  );

  // Compute all years covered by any deal (from min start year to max end year)
  function getAllCoveredYears(
    deals: Array<{
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    }>
  ) {
    if (deals.length === 0) return [];
    let minYear = Math.min(...deals.map(d => getYear(d.starts)));
    let maxYear = Math.max(...deals.map(d => getYear(d.ends)));
    // Also check if any deal starts in Dec and ends in Jan next year, so maxYear is at least the max end year
    return Array.from({ length: maxYear - minYear + 1 }, (_, i) => maxYear - i);
  }

  $: allYears = getAllCoveredYears(deals);

  // Timeline constants
  const months = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
  ];

  // For a given deal, year, and month, check if the deal covers any part of that month
  function dealCoversMonth(
    deal: {
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    },
    year: number,
    month: number
  ): boolean {
    const dealStart = parseLocalDate(deal.starts);
    const dealEnd = parseLocalDate(deal.ends);
    const monthStart = new Date(year, month, 1);
    const monthEnd = new Date(year, month, daysInMonth(year, month));
    return dealStart <= monthEnd && dealEnd >= monthStart;
  }

  // For a given year, build a 2D array: months[0..11] = array of deals covering that month
  function getMonthDeals(
    year: number,
    deals: Array<{
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    }>,
    prevYearDeals: Array<{
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    }> = [],
    nextYearDeals: Array<{
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    }> = []
  ) {
    return months.map((_, m) => {
      let monthDeals = deals.filter(deal => dealCoversMonth(deal, year, m));
      // For January, also check prevYearDeals that extend into this January
      if (m === 0 && prevYearDeals.length > 0) {
        monthDeals = monthDeals.concat(
          prevYearDeals.filter(deal => dealCoversMonth(deal, year, 0))
        );
      }
      // For December, also check nextYearDeals that start in December and extend into next year
      if (m === 11 && nextYearDeals.length > 0) {
        monthDeals = monthDeals.concat(
          nextYearDeals.filter(deal => dealCoversMonth(deal, year, 11))
        );
      }
      return monthDeals;
    });
  }

  let tooltip = {
    show: false,
    x: 0,
    y: 0,
    deal: null as null | (typeof deals)[0],
    monthIdx: 0,
  };

  // Detect mobile / narrow viewport
  let isMobile = false;

  function updateViewport() {
    isMobile = window.innerWidth <= 600;
  }

  onMount(() => {
    updateViewport();
    window.addEventListener('resize', updateViewport);
    return () => window.removeEventListener('resize', updateViewport);
  });

  // Reactive tooltip style string
  $: tooltipStyle = isMobile
    ? `top: ${tooltip.y + 12}px; left: 50%; transform: translateX(-50%);`
    : `top: ${tooltip.y + 12}px; left: ${tooltip.x + 12}px;`;

  function showTooltip(
    event: MouseEvent,
    deal: {
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    },
    monthIdx: number
  ) {
    tooltip = {
      show: true,
      x: event.clientX,
      y: event.clientY,
      deal,
      monthIdx,
    };
  }

  function hideTooltip() {
    tooltip.show = false;
  }

  // Helper: check if deal starts/ends in this month
  function isDealStartInMonth(
    deal: {
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    },
    year: number,
    month: number
  ) {
    const d = parseLocalDate(deal.starts);
    return d.getFullYear() === year && d.getMonth() === month;
  }
  function isDealEndInMonth(
    deal: {
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    },
    year: number,
    month: number
  ) {
    const d = parseLocalDate(deal.ends);
    return d.getFullYear() === year && d.getMonth() === month;
  }
  function isDealCoversWholeMonth(
    deal: {
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    },
    year: number,
    month: number
  ) {
    const monthStart = new Date(year, month, 1);
    const monthEnd = new Date(year, month, daysInMonth(year, month));
    // add for deal fully within the month
    return (
      (parseLocalDate(deal.starts) >= monthStart && parseLocalDate(deal.ends) <= monthEnd) ||
      (parseLocalDate(deal.starts) <= monthStart && parseLocalDate(deal.ends) >= monthEnd)
    );
  }
  function isDealFullyWithinMonth(
    deal: {
      starts: string;
      ends: string;
      discount: string;
      sale_type: 'dollar' | 'percent';
      channel: string | null;
      limit_qty: number | null;
      details: string | null;
    },
    year: number,
    month: number
  ) {
    const start = parseLocalDate(deal.starts),
      end = parseLocalDate(deal.ends),
      monthStart = new Date(year, month, 1),
      monthEnd = new Date(year, month, daysInMonth(year, month));
    return start >= monthStart && end <= monthEnd;
  }
</script>

<div class="history-card">
  <div class="header">
    <h2>{name}</h2>
    <span class="sku">SKU: {sku}</span>
  </div>
  {#if image_url && $loadPictures}
    <div class="product-image">
      <img src={image_url} alt={name} />
    </div>
  {/if}
  <div class="timeline-container">
    <div class="timeline-bar-row">
      <span class="year-label timeline-label-placeholder"></span>
      <div class="month-boxes">
        {#each months as month}
          <div class="month-box month-header">
            <span class="month-label long">{month}</span>
            <span class="month-label short">{month[0]}</span>
          </div>
        {/each}
      </div>
    </div>
    <div class="years-block">
      {#each allYears as year, rowIdx}
        <div class="year-row" style="z-index: {allYears.length - rowIdx}">
          <span class="year-label">{year}</span>
          <div class="month-boxes">
            {#each months as _, mIdx}
              {@const monthDeals = getMonthDeals(
                year,
                dealsByYear[year] ?? [],
                dealsByYear[year - 1] ?? [],
                dealsByYear[year + 1] ?? []
              )[mIdx]}
              {@const deal = monthDeals[0]}
              {#if monthDeals.length > 0}
                <div
                  role="tooltip"
                  class="month-box month-active {isDealFullyWithinMonth(deal, year, mIdx)
                    ? 'full'
                    : isDealCoversWholeMonth(deal, year, mIdx)
                      ? 'full'
                      : isDealStartInMonth(deal, year, mIdx)
                        ? 'triangle-lower'
                        : isDealEndInMonth(deal, year, mIdx)
                          ? 'triangle-upper'
                          : ''}"
                  on:mouseenter={e => showTooltip(e, deal, mIdx)}
                  on:mouseleave={hideTooltip}
                ></div>
              {:else}
                <div class="month-box"></div>
              {/if}
            {/each}
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>

{#if tooltip.show && tooltip.deal}
  <div class="deal-tooltip {isMobile ? 'mobile' : ''}" style={tooltipStyle}>
    <div class="tooltip-discount">
      <strong>{tooltip.deal.discount}</strong>
      {tooltip.deal.sale_type === 'percent' ? '%' : ''} OFF
    </div>
    <div>Valid: {tooltip.deal.starts} – {tooltip.deal.ends}</div>
    {#if tooltip.deal.limit_qty}
      <div>Limit: {tooltip.deal.limit_qty}</div>
    {/if}
    {#if tooltip.deal.channel}
      <div class="tooltip-channel">{tooltip.deal.channel}</div>
    {/if}
    {#if tooltip.deal.details}
      <div>{tooltip.deal.details}</div>
    {/if}
  </div>
{/if}

<style>
  .history-card {
    background: #fff;
    border-radius: 0.75rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
    padding: 1.5rem 2rem;
    margin: 1rem 0;
    max-width: 950px;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
  }
  .header {
    display: flex;
    align-items: baseline;
    gap: 1.2rem;
    margin-bottom: 0.5rem;
  }
  .header h2 {
    font-size: 1.3rem;
    font-weight: 700;
    margin: 0;
  }
  .sku {
    font-size: 0.95rem;
    color: #888;
  }
  .product-image {
    width: 100%;
    margin-bottom: 0.5rem;
  }
  .product-image img {
    width: 100%;
    height: auto;
    border-radius: 0.5rem;
    object-fit: cover;
  }
  .timeline-container {
    width: 100%;
    margin-top: 1.2rem;
    position: relative;
  }
  .timeline-bar-row {
    display: flex;
    align-items: center;
    width: 100%;
    margin-bottom: 0.3rem;
  }
  .timeline-label-placeholder {
    display: inline-block;
    width: 3.5rem;
    margin-right: 0.7rem;
    flex-shrink: 0;
  }
  .month-boxes {
    display: flex;
    flex-direction: row;
    gap: 0;
    width: 100%;
  }
  .month-box {
    flex: 1 1 0;
    min-width: 0;
    height: 2.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.4rem;
    background: #f8fafc;
    font-size: 1.05rem;
    font-weight: 500;
    color: #005fcc;
    border: 1px solid #e5e7eb;
    margin-right: -1px;
    position: relative;
    overflow: hidden;
    padding: 0 0.1rem;
  }
  .month-header {
    background: #f3f6fa;
    color: #1760c4;
    font-weight: 700;
    border-bottom: 2px solid #005fcc;
    height: 2.2rem;
  }
  .month-active {
    background: #1a7f37;
    color: #fff;
    border: 1.5px solid #1a7f37;
    z-index: 1;
  }
  .month-active.full {
    background: #1a7f37;
    color: #fff;
    border: 1.5px solid #1a7f37;
    z-index: 1;
  }
  .month-active.triangle-lower {
    background-color: #f8fafc;
    background: linear-gradient(to top left, #1a7f37 49%, #f8fafc 51%);
    color: #fff;
    border: 1px solid #e5e7eb;
    z-index: 1;
  }
  .month-active.triangle-upper {
    background-color: #f8fafc;
    background: linear-gradient(to bottom right, #1a7f37 49%, #f8fafc 51%);
    color: #fff;
    border: 1px solid #e5e7eb;
    z-index: 1;
  }
  .years-block {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    width: 100%;
  }
  .year-row {
    display: flex;
    align-items: center;
    position: relative;
    min-height: 2.2rem;
  }
  .year-label {
    width: 3.5rem;
    font-size: 1.05rem;
    font-weight: 600;
    color: #444;
    margin-right: 0.7rem;
    text-align: right;
    flex-shrink: 0;
  }
  @media (max-width: 900px) {
    .history-card {
      max-width: 100%;
      padding: 1rem 0.5rem;
    }
  }
  @media (max-width: 600px) {
    .month-box {
      font-size: 0.95rem;
      height: 2.2rem;
      padding: 0 0.1rem;
    }
    .month-header {
      height: 2.2rem;
    }
    .year-label {
      width: 2.2rem;
      font-size: 0.95rem;
    }
  }
  .deal-tooltip {
    position: fixed;
    z-index: 1000;
    background: #fff;
    color: #222;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.13);
    padding: 0.7rem 1rem;
    font-size: 1rem;
    pointer-events: none;
    min-width: 180px;
    max-width: 320px;
    white-space: pre-line;
  }
  .tooltip-discount {
    background: #1a7f37;
    color: #fff;
    border-radius: 0.5rem;
    padding: 0.2rem 0.8rem;
    font-size: 1.1rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 0.3rem;
  }
  .tooltip-channel {
    background: #e6f0fa;
    color: #1760c4;
    border-radius: 0.4rem;
    padding: 0.1rem 0.6rem;
    font-size: 0.98rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 0.2rem;
  }
  /* Month label visibility */
  .month-label.long {
    display: inline;
  }
  .month-label.short {
    display: none;
  }
  /* Switch to short label on small screens */
  @media screen and (max-width: 600px) {
    .month-label.long {
      display: none !important;
    }
    .month-label.short {
      display: inline !important;
    }
  }
  /* Mobile-specific overrides when tooltip centered */
  .deal-tooltip.mobile {
    max-width: 90vw;
  }
</style>
