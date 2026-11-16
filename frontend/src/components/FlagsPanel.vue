<script setup lang="ts">
import { computed } from "vue";

interface Flag {
  flag?: boolean;
  reason: string;
}

const props = defineProps<{ flags: Record<string, Flag | string> }>();

const titles: Record<string, string> = {
  cushion_breach: "Cash cushion",
  cushion_breach_worse_case: "Cash cushion, worst case",
  runway: "How long your cash lasts",
  expense_concentration: "One cost dominates",
  cost_creep: "Rising costs",
  revenue_volatility: "Income swings",
  fixed_cost_coverage: "Rent and payroll covered",
};

const cards = computed(() =>
  Object.entries(titles)
    .filter(([key]) => typeof props.flags[key] === "object")
    .map(([key, title]) => {
      const item = props.flags[key] as Flag;
      return { key, title, warn: item.flag === true, reason: item.reason };
    }),
);
</script>

<template>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
    <article
      v-for="card in cards"
      :key="card.key"
      class="rounded-lg border-s-4 p-3 text-sm"
      :class="
        card.warn
          ? 'border-amber-500 bg-amber-50'
          : 'border-emerald-500 bg-emerald-50'
      "
    >
      <h3 class="font-semibold">
        {{ card.warn ? "⚠ " : "✓ " }}{{ card.title }}
      </h3>
      <p class="mt-1 text-slate-700">{{ card.reason }}</p>
    </article>
  </div>
</template>
