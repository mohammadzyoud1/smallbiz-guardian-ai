<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
  Legend,
);

interface Forecast {
  weeks: number[];
  ending_cash: { low: number[]; forecast: number[]; high: number[] };
  cushion: number;
}

const props = defineProps<{ forecast: Forecast }>();
const canvas = ref<HTMLCanvasElement | null>(null);
let chart: Chart | null = null;

function draw() {
  if (!canvas.value) return;
  chart?.destroy();
  const f = props.forecast;
  chart = new Chart(canvas.value, {
    type: "line",
    data: {
      labels: f.weeks.map((w) => `Week ${w}`),
      datasets: [
        {
          label: "Best case",
          data: f.ending_cash.high,
          borderColor: "blue",

          fill: "+1",
          pointRadius: 0,
        },
        {
          label: "Expected",
          data: f.ending_cash.forecast,
          borderColor: "green",

          pointRadius: 2,
          fill: false,
        },
        {
          label: "Worst case",
          data: f.ending_cash.low,
          borderColor: "red",
          fill: false,
          pointRadius: 0,
        },
        {
          label: "Your cushion",
          data: f.weeks.map(() => f.cushion),
          borderColor: "black",
          borderDash: [6, 4],
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { ticks: { callback: (v) => "$" + Number(v).toLocaleString() } },
      },
      plugins: { legend: { position: "bottom" } },
    },
  });
}

onMounted(draw);
watch(() => props.forecast, draw);
onBeforeUnmount(() => chart?.destroy());
</script>

<template>
  <div class="h-64 w-full">
    <canvas ref="canvas"></canvas>
  </div>
</template>
