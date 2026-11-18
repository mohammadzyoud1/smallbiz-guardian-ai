<script setup lang="ts">
import { computed, ref } from "vue";
import { t } from "../i18n";

interface Message {
  role: "owner" | "guardian";
  text: string;
  exchangeId?: number;
  voted?: boolean;
  helpfulVote?: boolean;
}

const props = defineProps<{ sessionId: string }>();

const API = "http://127.0.0.1:8000";
const messages = ref<Message[]>([]);
const question = ref("");
const busy = ref(false);

const suggestions = [
  "What happens if sales drop 20 percent in December?",
  "Which expense should I look at first?",
  "Will I run low on cash?",
];

function clean(text: string) {
  return text.replace(/\*\*/g, "");
}

async function send(text: string) {
  const asked = text.trim();
  if (!asked || busy.value) return;
  messages.value.push({ role: "owner", text: asked });
  question.value = "";
  busy.value = true;
  try {
    const response = await fetch(`${API}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: props.sessionId, question: asked }),
    });
    if (response.status === 429) {
      messages.value.push({
        role: "guardian",
        text: "Too many questions at once. Please wait a minute and try again.",
      });
    } else if (response.status === 404) {
      messages.value.push({
        role: "guardian",
        text: "Your session has expired. Please upload your file again.",
      });
    } else if (!response.ok) {
      messages.value.push({
        role: "guardian",
        text: "Something went wrong. Please try again.",
      });
    } else {
      const data = await response.json();
      messages.value.push({
        role: "guardian",
        text: clean(data.answer),
        exchangeId: data.exchange_id,
      });
    }
  } catch {
    messages.value.push({
      role: "guardian",
      text: "Could not reach the server. Please try again.",
    });
  } finally {
    busy.value = false;
  }
}

async function vote(message: Message, helpful: boolean) {
  if (message.exchangeId === undefined || message.voted) return;
  await fetch(`${API}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ exchange_id: message.exchangeId, helpful }),
  });
  message.voted = true;
  message.helpfulVote = helpful;
}
const askPlaceholder = computed(() => t("askPlaceholder"));
</script>

<template>
  <div>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="s in suggestions"
        :key="s"
        :disabled="busy"
        class="min-h-11 rounded-full border border-emerald-600 px-3 py-2 text-start text-sm text-emerald-700 disabled:opacity-50"
        @click="send(s)"
      >
        {{ s }}
      </button>
    </div>

    <div class="mt-4 flex flex-col gap-3">
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="max-w-[90%] whitespace-pre-line rounded-2xl px-3 py-2 text-sm"
        :class="
          m.role === 'owner'
            ? 'self-end bg-emerald-600 text-white'
            : 'self-start bg-slate-100'
        "
      >
        {{ m.text }}
        <div
          v-if="m.role === 'guardian' && m.exchangeId !== undefined"
          class="mt-2 flex gap-2"
        >
          <button
            v-if="!m.voted || m.helpfulVote === true"
            class="min-h-11 min-w-11 rounded-lg bg-white text-lg"
            :class="m.voted ? 'bg-emerald-100 ring-2 ring-emerald-500' : ''"
            :disabled="m.voted"
            @click="vote(m, true)"
          >
            👍
          </button>

          <button
            v-if="!m.voted || m.helpfulVote === false"
            class="min-h-11 min-w-11 rounded-lg bg-white text-lg"
            :class="m.voted ? 'bg-red-100 ring-2 ring-red-500' : ''"
            :disabled="m.voted"
            @click="vote(m, false)"
          >
            👎
          </button>
        </div>
      </div>
      <p v-if="busy" class="text-sm text-slate-500">
        The Guardian is looking at your numbers. This can take up to a minute...
      </p>
    </div>

    <form class="mt-4 flex gap-2" @submit.prevent="send(question)">
      <input
        v-model="question"
        type="text"
        :placeholder="askPlaceholder"
        class="min-h-11 min-w-0 flex-1 rounded-lg border border-slate-300 px-3 text-sm"
      />
      <button
        type="submit"
        :disabled="busy"
        class="min-h-11 rounded-lg bg-emerald-600 px-4 text-sm font-medium text-white disabled:opacity-50"
      >
        {{ t("ask") }}
      </button>
    </form>
  </div>
</template>
