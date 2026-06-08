# Nunabot

## Overview
A **Solana-native GPU bot protocol** — a bot-first compute marketplace connecting users, AI agents,
and GPU providers. The bot prices a task, the router picks a provider by **reputation**, the job runs
and settles in **SOL**, and the provider's reputation updates from the result. AI agents run jobs
autonomously against a prepaid **budget session**.

## Stack
- **Backend**: Python 3.11, Flask 3.0, httpx
- **Frontend**: Vue 3 + Vite
- **AI**: Anthropic Claude (primary), DeepInfra/OpenAI-compatible (fallback)

## Structure
```
backend/app/services/
  solana_client.py  — SOL/USD oracle (fallback so dev/tests need no network)
  catalog.py        — task types (inference/generation/analysis/automation/market)
  pricing.py        — compute_units × baseline × demand → SOL
  providers.py      — provider registry + reputation from 5 signals [core]
  router.py         — reputation-weighted routing (rep × free capacity) [core]
  jobs.py           — lifecycle: quote → submit → complete/fail; settle + rep update [core]
  agents.py         — agent budget sessions: autonomous job chaining [distinct]
  planner.py        — bot agent: NL → task spec + quote (LLM)
  registry.py       — shared singletons
```

## Reputation (the differentiator)
`reputation = 1000 × Σ wᵢ·signalᵢ` over reliability(.30), uptime(.25), speed(.20), quality(.15),
volume(.10). Each signal 0..1, derived from raw counters (heartbeats, completed/failed, speed ratio
samples, quality samples). Score → tier (new/rising/trusted/elite) → routing priority + earnings
bonus (≤ +10%).

## Routing
`score = ROUTING_REP_WEIGHT × rep_frac + (1−weight) × capacity_frac`, over providers with a free GPU.
Reputation dominates; capacity breaks ties and load-balances.

## Job flow
quote (compute units × demand) → submit (router.pick, occupy GPU) → complete (pay provider net+bonus,
free GPU, feed speed/quality into reputation) OR fail (free GPU, hit reliability).

## Agent layer
`open_session(budget)` → `run(task)` debits the session and chains jobs until the budget can't cover
the next one. Makes Nunabot a programmable execution backend for autonomous agents.

## Dev
```bash
npm run dev                          # both servers
pytest tests/ -v                     # no API keys (SOL price mocked)
python backend/scripts/simulate.py   # providers build rep, bot runs jobs, agent chains
```
Tests cover reputation scoring, reputation-weighted routing, the job lifecycle (settle, bonus, rep
update), pricing/catalog, and the agent session layer.

## Note on git
Commits authored anonymously as the project (no personal contributor).
