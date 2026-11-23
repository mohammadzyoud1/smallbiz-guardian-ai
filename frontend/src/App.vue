<script setup lang="ts">
import { ref } from "vue";
import ForecastChart from "./components/ForecastChart.vue";
import FlagsPanel from "./components/FlagsPanel.vue";
import ScenarioCard from "./components/ScenarioCard.vue";
import ScenarioChart from "./components/ScenarioChart.vue";
import ChatPanel from "./components/ChatPanel.vue";
import { t, toggleLanguage, translateMessage } from "./i18n";
interface ReportMessage {
  code: string;
  params: Record<string, string | number>;
}
interface QualityReport {
  file: string;
  passed: boolean;
  errors: ReportMessage[];
  warnings: ReportMessage[];
  info: ReportMessage[];
  forecast_ready: ReportMessage;
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
    console.log("Uploading:", file.name);
    const response = await fetch(`${API}/upload`, {
      method: "POST",
      body: formData,
    });
    const data: UploadResponse = await response.json();
    console.log("Upload response:", data);
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }
    report.value = data.report;
    sessionId.value = data.session_id;
    weeks.value = data.weeks ?? 0;
    if (!data.report) {
      throw new Error("Upload response does not contain a report.");
    }
    console.log(`errors : ${report.value.errors}`);
    console.log(`report value :${report.value}`);
    if (data.session_id && report.value.errors.length === 0) {
      await Promise.all([
        loadForecast(data.session_id),
        loadFlags(data.session_id),
      ]);
      console.log("Forecast and flags loaded successfully.");
    }
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

const scenarioResult = ref<any>(null);
</script>

<template>
  <main class="mx-auto min-h-screen max-w-xl bg-slate-50 p-4 text-slate-800">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">{{ t("title") }}</h1>
      <button
        class="min-h-11 rounded-lg border border-slate-300 px-3 text-sm"
        @click="toggleLanguage"
      >
        {{ t("language") }}
      </button>
    </div>
    <p class="mt-1 text-xs text-slate-500">{{ t("disclaimer") }}</p>

    <section class="mt-4 rounded-xl bg-white p-4 shadow-sm">
      <h2 class="mb-3 text-lg font-semibold">
        {{ t("upload") }}
      </h2>
      <label
        class="flex min-h-11 cursor-pointer items-center justify-center rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
      >
        {{ t("choosefile") }}
        <input
          type="file"
          accept=".csv,.xlsx"
          :disabled="busy"
          @change="onFile"
          class="hidden"
        />
      </label>
      <p class="mt-3 text-sm text-slate-600">
        {{ t("needTemplate") }}
        <a
          href="/templates/template_v1_example.csv"
          download
          class="text-emerald-700 underline"
          >CSV</a
        >
        ·
        <a
          href="/templates/template_v1_example.xlsx"
          download
          class="text-emerald-700 underline"
          >Excel</a
        >
      </p>
      <p v-if="busy" class="mt-3 text-sm text-slate-500">
        {{ t("checking") }}
      </p>
      <p v-if="problem" class="mt-3 text-sm text-red-700">{{ problem }}</p>
    </section>

    <section v-if="report" class="mt-4 rounded-xl bg-white p-4 shadow-sm">
      <h2 class="mb-2 text-lg font-semibold">{{ t("dataCheck") }}</h2>
      <p
        :class="report.passed ? 'text-emerald-700' : 'text-red-700'"
        class="font-medium"
      >
        {{ report.passed ? t("ready") : t("needsFixes") }}
      </p>
      <p class="mt-1 text-sm text-slate-600">
        {{
          translateMessage(
            report.forecast_ready.code,
            report.forecast_ready.params,
          )
        }}
      </p>

      <div v-if="report.errors.length" class="mt-3">
        <h3 class="font-semibold text-red-700">{{ t("pleaseFix") }}</h3>
        <ul class="ms-5 list-disc text-sm">
          <li v-for="(item, index) in report.errors" :key="index">
            {{ translateMessage(item.code, item.params) }}
          </li>
        </ul>
      </div>
      <div v-if="report.warnings.length" class="mt-3">
        <h3 class="font-semibold text-amber-700">{{ t("worthLook") }}</h3>
        <ul class="ms-5 list-disc text-sm">
          <li v-for="(item, index) in report.warnings" :key="index">
            {{ translateMessage(item.code, item.params) }}
          </li>
        </ul>
      </div>
      <ul
        v-if="report.info.length"
        class="ms-5 mt-3 list-disc text-sm text-slate-600"
      >
        <li v-for="(item, index) in report.info" :key="index">
          {{ translateMessage(item.code, item.params) }}
        </li>
      </ul>
    </section>

    <p v-if="sessionId" class="mt-4 text-sm font-medium text-emerald-700">
      {{ t("session") }} {{ weeks }} {{ t("weeksLoaded") }}
    </p>

    <section
      v-if="forecast && report && report.errors.length === 0"
      class="mt-4 rounded-xl bg-white p-4 shadow-sm"
    >
      <h2 class="mb-2 text-lg font-semibold">{{ t("forecastTitle") }}</h2>
      <ForecastChart :forecast="forecast" />
      <p class="mt-2 text-xs text-slate-500">
        {{ t("forecastNote") }}
      </p>
    </section>
    <section
      v-if="flags && report && report.errors.length === 0"
      class="mt-4 rounded-xl bg-white p-4 shadow-sm"
    >
      <h2 class="mb-3 text-lg font-semibold">{{ t("flagsTitle") }}</h2>
      <FlagsPanel :flags="flags" />
    </section>

    <section
      v-if="sessionId && report && report.errors.length === 0"
      class="mt-4"
    >
      <h2 class="mb-3 text-lg font-semibold">{{ t("scenariosTitle") }}</h2>
      <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
        <ScenarioCard
          title="slowSeasonTitle"
          help="slowSeasonHelp"
          scenario="slow_season"
          :session-id="sessionId"
          :sliders="[
            {
              key: 'drop',
              label: t('salesDrop'),
              min: 0.05,
              max: 0.5,
              step: 0.05,
              value: 0.2,
            },
            {
              key: 'start',
              label: t('startsInWeek'),
              min: 1,
              max: 13,
              step: 1,
              value: 3,
            },
            {
              key: 'length',
              label: t('lastsWeeks'),
              min: 1,
              max: 13,
              step: 1,
              value: 4,
            },
          ]"
          @result="scenarioResult = $event"
        />
        <ScenarioCard
          title="costShockTitle"
          help="costShockHelp"
          scenario="cost_shock"
          :session-id="sessionId"
          :sliders="[
            {
              key: 'amount',
              label: t('costAmount'),
              min: 100,
              max: 10000,
              step: 100,
              value: 2000,
            },
            {
              key: 'week',
              label: t('inWeek'),
              min: 1,
              max: 13,
              step: 1,
              value: 4,
            },
          ]"
          @result="scenarioResult = $event"
        />
        <ScenarioCard
          title="priceChangeTitle"
          help="priceChangeHelp"
          scenario="decision_lever"
          :session-id="sessionId"
          :sliders="[
            {
              key: 'price_change',
              label: 'priceChange',
              min: -0.2,
              max: 0.3,
              step: 0.05,
              value: 0.05,
            },
            {
              key: 'demand_response',
              label: t('customerReaction'),
              min: 0,
              max: 1,
              step: 0.5,
              value: 0.5,
            },
            {
              key: 'extra_cost',
              label: t('addedWeeklyCost'),
              min: 0,
              max: 2000,
              step: 100,
              value: 0,
            },
          ]"
          @result="scenarioResult = $event"
        />
      </div>

      <div
        v-if="scenarioResult && forecast"
        class="mt-3 rounded-xl bg-white p-4 shadow-sm"
      >
        <h3 class="mb-2 text-base font-semibold">
          {{ t(scenarioResult.title) }}: {{ t("cashCompared") }}
        </h3>
        <ScenarioChart
          :baseline="scenarioResult.ending_cash.baseline"
          :scenario="scenarioResult.ending_cash.scenario"
          :cushion="forecast.cushion"
        />
      </div>
    </section>
    <section
      v-if="sessionId && report && report.errors.length === 0"
      class="mt-4 rounded-xl bg-white p-4 shadow-sm"
    >
      <h2 class="mb-3 text-lg font-semibold">{{ t("askTitle") }}</h2>
      <div class="mb-2">
        <strong>{{ t("guardlang") }}</strong>
      </div>
      <ChatPanel :session-id="sessionId" />
      <p class="mt-3 text-xs text-slate-500">
        SmallBiz Guardian AI is an educational planning tool. It is not
        financial, legal, or tax advice.
      </p>
    </section>
  </main>
</template>
