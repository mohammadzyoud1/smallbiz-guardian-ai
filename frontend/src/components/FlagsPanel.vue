<script setup lang="ts">
import { computed } from "vue";
import { t, translateMessage, type Key } from "../i18n";
interface Message {
  code: string;
  params: Record<string, string | number>;
}
interface Flag {
  flag?: boolean;
  reason: Message;
}

const props = defineProps<{ flags: Record<string, Flag | string> }>();

const titles: Record<string, Key> = {
  cushion_breach: "cashCushion",
  cushion_breach_worse_case: "cashCushionWorstCase",
  runway: "cashRunway",
  expense_concentration: "expenseConcentration",
  cost_creep: "risingCosts",
  revenue_volatility: "incomeSwings",
  fixed_cost_coverage: "fixedCostCoverage",
};

const cards = computed(() =>
  Object.entries(titles)
    .filter(([key]) => typeof props.flags[key] === "object")
    .map(([key, title]) => {
      const item = props.flags[key] as Flag;
      return {
        key,
        title: t(title),
        warn: item.flag === true,
        reason: translateMessage(item.reason.code, item.reason.params),
      };
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
