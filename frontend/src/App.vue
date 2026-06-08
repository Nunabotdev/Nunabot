<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="shell">
    <header>
      <div class="brand">
        <span class="mark"></span>
        <span class="name">Nunabot</span>
      </div>
      <nav>
        <RouterLink to="/bot">Bot</RouterLink>
        <RouterLink to="/providers">Providers</RouterLink>
        <RouterLink to="/agents">Agents</RouterLink>
      </nav>
      <span class="tag">Solana GPU bot protocol</span>
    </header>
    <main><RouterView /></main>
  </div>
</template>

<style>
:root {
  --bg: #0c0a16;
  --panel: #16122a;
  --line: #271f44;
  --text: #ece9f6;
  --muted: #9b91bd;
  --accent: #a855f7;
  --accent2: #38bdf8;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
.shell { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
header { display: flex; align-items: center; gap: 24px; padding: 20px 0; border-bottom: 1px solid var(--line); }
.brand { display: flex; align-items: center; gap: 10px; }
.mark { width: 22px; height: 22px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #c084fc, #7c3aed 60%, #38bdf8); }
.name { font-weight: 700; font-size: 19px; letter-spacing: -0.02em; }
nav { display: flex; gap: 6px; }
nav a { color: var(--muted); text-decoration: none; padding: 7px 14px; border-radius: 8px; font-size: 14px; }
nav a:hover { color: var(--text); background: var(--panel); }
nav a.router-link-active { color: var(--accent); background: var(--panel); }
.tag { margin-left: auto; color: var(--muted); font-size: 13px; }
main { padding: 28px 0 60px; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 20px; margin-bottom: 18px; }
h2 { margin: 0 0 4px; font-size: 20px; letter-spacing: -0.02em; }
.sub { color: var(--muted); font-size: 14px; margin: 0 0 18px; }
label { display: block; font-size: 13px; color: var(--muted); margin: 12px 0 6px; }
input, select { width: 100%; background: #0d0a1c; border: 1px solid var(--line); color: var(--text);
  padding: 11px 12px; border-radius: 9px; font-size: 14px; }
button { background: var(--accent); color: #1a0b2e; border: none; padding: 11px 18px;
  border-radius: 9px; font-weight: 700; cursor: pointer; font-size: 14px; margin-top: 16px; }
button:hover { filter: brightness(1.08); }
button.ghost { background: transparent; border: 1px solid var(--line); color: var(--text); }
.row { display: flex; gap: 14px; flex-wrap: wrap; }
.row > * { flex: 1; min-width: 150px; }
.stat { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed var(--line); font-size: 14px; }
.stat:last-child { border-bottom: none; }
.stat b { color: var(--accent); }
.pill { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.pill.elite { background: #2a1245; color: #d8b4fe; }
.pill.trusted { background: #102a3a; color: #7dd3fc; }
.pill.rising { background: #112a1e; color: #6ee7b7; }
.pill.new { background: #241f33; color: #c4b5e0; }
.err { color: #f87171; font-size: 13px; margin-top: 10px; }
.muted { color: var(--muted); font-size: 13px; }
pre { background: #0d0a1c; border: 1px solid var(--line); border-radius: 9px; padding: 14px;
  overflow-x: auto; font-size: 12.5px; color: #cbd5e1; }
.bar { height: 7px; background: #0d0a1c; border-radius: 999px; overflow: hidden; }
.bar > span { display: block; height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); }
</style>
