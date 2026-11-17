<script setup lang="ts">
import { reactive, ref, watch } from "vue";

interface Slider {
  key: string;
  label: string;
  min: number;
  max: number;
  step: number;
  value: number;
}

const props = defineProps<{
  title: string;
  help: string;
  scenario: string;
  sessionId: string;
  sliders: Slider[];
  fixed?: Record<string, unknown>;
}>();
const emit = defineEmits<{ (e: "result", value: any): void }>();

const API = "http://127.0.0.1:8000";
const values = reactive<Record<string, number>>(
  Object.fromEntries(props.sliders.map((s) => [s.key, s.value])),
);
const summary = ref<any>(null);
let timer: number | undefined;

async function run() {
  const response = await fetch(`${API}/scenario`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: props.sessionId,
      name: props.scenario,
      ...props.fixed,
      ...values,
    }),
  });
  summary.value = await response.json();
  emit("result", { ...summary.value, title: props.title });
}

watch(values, () => {
  clearTimeout(timer);
  timer = window.setTimeout(run, 300);
});
run();

function money(n: number) {
  return (n < 0 ? "-$" : "+$") + Math.abs(Math.round(n)).toLocaleString();
}
</script>

<template>
  <article class="rounded-xl bg-white p-4 shadow-sm">
    <h3 class="text-base font-semibold">{{ title }}</h3>
    <p class="mt-1 text-xs text-slate-500">{{ help }}</p>

    <div v-for="s in sliders" :key="s.key" class="mt-4">
      <label class="flex justify-between text-sm">
        <span>{{ s.label }}</span>
        <span class="font-medium">{{ values[s.key] }}</span>
      </label>
      <input
        type="range"
        :min="s.min"
        :max="s.max"
        :step="s.step"
        v-model.number="values[s.key]"
        class="mt-1 h-8 w-full accent-emerald-600"
      />
    </div>

    <p v-if="summary" class="mt-4 rounded-lg bg-slate-50 p-3 text-sm">
      Lowest cash: <strong>{{ money(summary.change.lowest_cash) }}</strong
      ><br />
      13-week net: <strong>{{ money(summary.change.net_13_weeks) }}</strong>
    </p>
  </article>
</template>
