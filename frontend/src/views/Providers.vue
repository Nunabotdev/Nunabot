<script setup>
import { ref, onMounted } from "vue";
import api from "../api";

const operator = ref("my.gpu.farm");
const gpus = ref(4);
const list = ref([]);
const err = ref("");

const labels = {
  uptime: "Uptime", speed: "Speed", reliability: "Reliability",
  volume: "Volume", quality: "Quality",
};

async function refresh() {
  try { list.value = await api.providers(true); }
  catch (e) { err.value = e.response?.data?.error || e.message; }
}

async function register() {
  err.value = "";
  try { await api.registerProvider(operator.value, Number(gpus.value)); await refresh(); }
  catch (e) { err.value = e.response?.data?.error || e.message; }
}

onMounted(refresh);
</script>

<template>
  <div class="card">
    <h2>Supply GPU power</h2>
    <p class="sub">Register idle GPUs, complete jobs, and build reputation from uptime, speed, reliability, and quality.</p>
    <div class="row">
      <div><label>Operator</label><input v-model="operator" /></div>
      <div><label>GPUs</label><input type="number" v-model="gpus" /></div>
    </div>
    <button @click="register">Register</button>
  </div>

  <div class="card" v-if="list.length">
    <h2>Reputation leaderboard</h2>
    <p class="sub">Routing favors higher reputation — but only providers with free capacity.</p>
    <div v-for="p in list" :key="p.id" style="border-bottom:1px solid var(--line);padding:14px 0">
      <div style="display:flex;align-items:center;justify-content:space-between">
        <strong>{{ p.operator }}</strong>
        <span class="pill" :class="p.tier">{{ p.tier }} · {{ p.reputation }}</span>
      </div>
      <div class="muted" style="margin:6px 0 10px">
        {{ p.available }}/{{ p.gpus }} free · {{ p.completed_jobs }} jobs ·
        +{{ (p.earnings_bonus * 100).toFixed(1) }}% earnings · {{ p.earnings_sol }} SOL earned
      </div>
      <div v-for="(v, k) in p.components" :key="k" style="display:flex;align-items:center;gap:10px;margin:5px 0">
        <span class="muted" style="width:90px">{{ labels[k] }}</span>
        <div class="bar" style="flex:1"><span :style="{ width: (v * 100) + '%' }"></span></div>
        <span class="muted" style="width:38px;text-align:right">{{ (v * 100).toFixed(0) }}%</span>
      </div>
    </div>
  </div>

  <p class="err" v-if="err">{{ err }}</p>
</template>
