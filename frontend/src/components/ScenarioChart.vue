<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
} from "chart.js";

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
);

const props = defineProps<{
  baseline: number[];
  scenario: number[];
  cushion: number;
}>();
const canvas = ref<HTMLCanvasElement | null>(null);
let chart: Chart | null = null;

function draw() {
  if (!canvas.value) return;
  chart?.destroy();
  chart = new Chart(canvas.value, {
    type: "line",
    data: {
      labels: props.baseline.map((_, i) => `Week ${i + 1}`),
      datasets: [
        {
          label: "Without the change",
          data: props.baseline,
          borderColor: "#94a3b8",
          pointRadius: 0,
        },
        {
          label: "With the change",
          data: props.scenario,
          borderColor: "#059669",
          pointRadius: 2,
        },
        {
          label: "Your cushion",
          data: props.baseline.map(() => props.cushion),
          borderColor: "#dc2626",
          borderDash: [6, 4],
          pointRadius: 0,
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
watch(() => [props.baseline, props.scenario], draw);
onBeforeUnmount(() => chart?.destroy());
</script>

<template>
  <div class="h-64 w-full">
    <canvas ref="canvas"></canvas>
  </div>
</template>
