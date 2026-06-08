<script setup>
import { ref } from "vue";
import api from "../api";

const agent = ref("agent.zeta");
const budget = ref(0.05);
const session = ref(null);
const task = ref("inference");
const err = ref("");

async function open() {
  err.value = "";
  try { session.value = await api.openSession(agent.value, Number(budget.value)); }
  catch (e) { err.value = e.response?.data?.error || e.message; }
}

async function run() {
  err.value = "";
  try {
    const res = await api.runSession(session.value.id, task.value, 1);
    session.value = res.session;
  } catch (e) { err.value = e.response?.data?.error || e.message; }
}
</script>

<template>
  <div class="card">
    <h2>Agent execution layer</h2>
    <p class="sub">Open a budget session, then let an agent autonomously chain GPU jobs until the budget runs out.</p>
    <div class="row">
      <div><label>Agent</label><input v-model="agent" /></div>
      <div><label>Budget (SOL)</label><input type="number" step="0.01" v-model="budget" /></div>
    </div>
    <button @click="open">Open session</button>
  </div>

  <div class="card" v-if="session">
    <h2>Session {{ session.id }}</h2>
    <div class="stat"><span>Budget</span><b>{{ session.budget_sol }} SOL</b></div>
    <div class="stat"><span>Spent</span><b>{{ session.spent_sol }} SOL</b></div>
    <div class="stat"><span>Remaining</span><b>{{ session.remaining_sol }} SOL</b></div>
    <div class="stat"><span>Jobs run</span><b>{{ session.jobs }}</b></div>
    <div class="bar" style="margin-top:12px">
      <span :style="{ width: (session.spent_sol / session.budget_sol * 100) + '%' }"></span>
    </div>
    <div class="row" style="margin-top:16px">
      <div>
        <label>Next task</label>
        <select v-model="task">
          <option value="inference">inference</option>
          <option value="generation">generation</option>
          <option value="analysis">analysis</option>
          <option value="automation">automation</option>
          <option value="market">market</option>
        </select>
      </div>
    </div>
    <button @click="run" :disabled="session.status !== 'open'">Run one job</button>
  </div>

  <p class="err" v-if="err">{{ err }}</p>
</template>
