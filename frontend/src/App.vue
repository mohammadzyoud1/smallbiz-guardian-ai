<script setup lang="ts">
import { ref } from "vue";
import ForecastChart from "./components/ForecastChart.vue";
import FlagsPanel from "./components/FlagsPanel.vue";
interface QualityReport {
  file: string;
  passed: boolean;
  errors: string[];
  warnings: string[];
  info: string[];
  forecast_ready: string;
}

interface UploadResponse {
  session_id: string | null;
  weeks?: number;
  report: QualityReport;
}

const API = "http://127.0.0.1:8000";
const sessionId = ref<string | null>(null);
const report = ref<QualityReport | null>(null);
const weeks = ref(0);
const busy = ref(false);
const problem = ref("");

async function onFile(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  busy.value = true;
  problem.value = "";
  report.value = null;
  sessionId.value = null;
  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API}/upload`, {
      method: "POST",
      body: formData,
    });
    const data: UploadResponse = await response.json();
    report.value = data.report;
    sessionId.value = data.session_id;
    weeks.value = data.weeks ?? 0;
    console.log(`errors : ${report.value.errors}`);
    console.log(`report value :${report.value}`);
    if (data.session_id && report.value.errors.length === 0)
      await Promise.all([
        loadForecast(data.session_id),
        loadFlags(data.session_id),
      ]);
  } catch {
    problem.value = "Could not reach the server. Please try again.";
  } finally {
    busy.value = false;
  }
}

const forecast = ref<any>(null);

async function loadForecast(id: string) {
  const response = await fetch(`${API}/forecast?session_id=${id}`);
  forecast.value = await response.json();
}

const flags = ref<any>(null);

async function loadFlags(id: string) {
  const response = await fetch(`${API}/flags?session_id=${id}`);
  flags.value = await response.json();
}
</script>

<template>
  <main class="mx-auto min-h-screen max-w-xl bg-slate-50 p-4 text-slate-800">
    <h1 class="text-2xl font-bold">SmallBiz Guardian AI</h1>
    <p class="mt-1 text-xs text-slate-500">
      SmallBiz Guardian AI is an educational planning tool. It is not financial,
      legal, or tax advice.
    </p>

    <section class="mt-4 rounded-xl bg-white p-4 shadow-sm">
      <h2 class="mb-3 text-lg font-semibold">
        1. Upload your sales and expenses
      </h2>
      <input
        type="file"
        accept=".csv,.xlsx"
        :disabled="busy"
        @change="onFile"
        class="block w-full text-sm file:me-3 file:rounded-lg file:border-0 file:bg-emerald-600 file:px-4 file:py-2 file:text-white"
      />
      <p v-if="busy" class="mt-3 text-sm text-slate-500">
        Checking your file...
      </p>
      <p v-if="problem" class="mt-3 text-sm text-red-700">{{ problem }}</p>
    </section>

    <section v-if="report" class="mt-4 rounded-xl bg-white p-4 shadow-sm">
      <h2 class="mb-2 text-lg font-semibold">Data check</h2>
      <p
        :class="report.passed ? 'text-emerald-700' : 'text-red-700'"
        class="font-medium"
      >
        {{
          report.passed
            ? "Your file is ready."
            : "Your file needs fixes before we can forecast."
        }}
      </p>
      <p class="mt-1 text-sm text-slate-600">{{ report.forecast_ready }}</p>

      <div v-if="report.errors.length" class="mt-3">
        <h3 class="font-semibold text-red-700">Please fix</h3>
        <ul class="ms-5 list-disc text-sm">
          <li v-for="item in report.errors" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div v-if="report.warnings.length" class="mt-3">
        <h3 class="font-semibold text-amber-700">Worth a look</h3>
        <ul class="ms-5 list-disc text-sm">
          <li v-for="item in report.warnings" :key="item">{{ item }}</li>
        </ul>
      </div>
      <ul
        v-if="report.info.length"
        class="ms-5 mt-3 list-disc text-sm text-slate-600"
      >
        <li v-for="item in report.info" :key="item">{{ item }}</li>
      </ul>
    </section>

    <p v-if="sessionId" class="mt-4 text-sm font-medium text-emerald-700">
      Session started. {{ weeks }} weeks of data loaded.
    </p>

    <section
      v-if="forecast && report && report.errors.length === 0"
      class="mt-4 rounded-xl bg-white p-4 shadow-sm"
    >
      <h2 class="mb-2 text-lg font-semibold">2. Your next 13 weeks</h2>
      <ForecastChart :forecast="forecast" />
      <p class="mt-2 text-xs text-slate-500">
        The shaded area is a range of likely outcomes. It is an estimate, not a
        promise.
      </p>
    </section>
    <section
      v-if="flags && report && report.errors.length === 0"
      class="mt-4 rounded-xl bg-white p-4 shadow-sm"
    >
      <h2 class="mb-3 text-lg font-semibold">3. Things to watch</h2>
      <FlagsPanel :flags="flags" />
    </section>
  </main>
</template>
