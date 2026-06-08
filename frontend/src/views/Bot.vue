<script setup>
import { ref, onMounted } from "vue";
import api from "../api";

const requester = ref("user.demo");
const taskKey = ref("inference");
const units = ref(1);
const tasks = ref([]);
const quote = ref(null);
const message = ref("generate an image of a neon city");
const result = ref(null);
const err = ref("");

onMounted(async () => {
  try { tasks.value = await api.catalog(); } catch (e) { /* ignore */ }
});

async function getQuote() {
  err.value = "";
  try { quote.value = await api.botQuote(taskKey.value, Number(units.value)); }
  catch (e) { err.value = e.response?.data?.error || e.message; }
}

async function submitJob() {
  err.value = "";
  try {
    const job = await api.submit(requester.value, taskKey.value, Number(units.value));
    result.value = await api.complete(job.id, 0.92);
  } catch (e) { err.value = e.response?.data?.error || e.message; }
}

async function runBot() {
  err.value = "";
  try { result.value = await api.botRequest(message.value); }
  catch (e) { err.value = e.response?.data?.error || e.message; }
}
</script>

<template>
  <div class="card">
    <h2>Run a GPU task</h2>
    <p class="sub">Request inference, generation, analysis, automation, or market processing — paid in SOL.</p>
    <div class="row">
      <div><label>Requester</label><input v-model="requester" /></div>
      <div>
        <label>Task</label>
        <select v-model="taskKey">
          <option v-for="t in tasks" :key="t.key" :value="t.key">
            {{ t.label }} · {{ t.sol_cost }} SOL
          </option>
        </select>
      </div>
      <div><label>Units</label><input type="number" step="0.5" v-model="units" /></div>
    </div>
    <div style="display:flex;gap:12px">
      <button @click="getQuote">Quote</button>
      <button class="ghost" @click="submitJob">Submit + run</button>
    </div>
  </div>

  <div class="card" v-if="quote">
    <h2>Quote</h2>
    <div class="stat"><span>Compute units</span><b>{{ quote.compute_units }}</b></div>
    <div class="stat"><span>Demand multiplier</span><b>{{ quote.demand_multiplier }}×</b></div>
    <div class="stat"><span>USD cost</span><b>${{ quote.usd_cost }}</b></div>
    <div class="stat"><span>SOL cost</span><b>{{ quote.sol_cost }} SOL</b></div>
  </div>

  <div class="card">
    <h2>Ask the bot</h2>
    <p class="sub">Plain language → a routed, priced GPU task.</p>
    <input v-model="message" />
    <button class="ghost" @click="runBot">Plan task</button>
    <p class="muted" style="margin-top:10px">Needs NUNA_LLM_API_KEY on the backend.</p>
  </div>

  <div class="card" v-if="result">
    <h2>Result</h2>
    <pre>{{ JSON.stringify(result, null, 2) }}</pre>
  </div>

  <p class="err" v-if="err">{{ err }}</p>
</template>
