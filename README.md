<img width="1070" height="705" alt="image" src="https://github.com/user-attachments/assets/27780d30-c420-4e03-ba2d-b9db9d5ea804" />


**A Solana-native GPU bot protocol.** A bot-first compute marketplace that connects users, AI agents,
and GPU providers. Request an AI task through a bot, Nunabot prices it, routes it to the best provider
by reputation, tracks execution, and settles payment in SOL. Providers earn by supplying idle compute
and build a reputation that wins them more work.

---

## Why Nunabot

GPU capacity is scattered and hard to reach, and most compute markets route blindly to whoever is
free. Nunabot makes the network **reputation-aware**: the providers who are reliable, fast, and
high-quality earn a better score, win routing, and net an earnings bonus. The result is a liquid,
accessible compute layer where good operators rise and requesters get dependable execution.

## How it works

```
   user / AI agent
        │  "run this task"
        ▼
   bot  → price the job (compute units × demand, in SOL)
        ▼
   router → pick provider by reputation × free capacity
        ▼
   provider runs it → execution tracked → SOL settled
        ▲                                   │
        └── reputation updated (uptime, speed, reliability, quality)
```

## Provider reputation (the core)

Every provider earns a reputation score (0–1000) from five live signals:

| Signal | Weight | What it measures |
|---|---|---|
| Reliability | 30% | completed vs failed jobs |
| Uptime | 25% | heartbeats seen vs expected |
| Speed | 20% | actual vs estimated runtime |
| Quality | 15% | average output-quality rating |
| Volume | 10% | completed jobs (log-scaled) |

Score → tier (**new** / **rising** / **trusted** / **elite**) → **routing priority** and an
**earnings bonus** of up to +10%. Reputation is always derived from raw signals, never stored, so the
formula can evolve.

## Reputation-weighted routing

The router scores each provider with free capacity as
`ROUTING_REP_WEIGHT × reputation + (1 − weight) × free_capacity`. High reputation wins, but a provider
must have a GPU free to be eligible, and spare capacity breaks ties so the network load-balances.

## Job lifecycle

`quote → submit (route + occupy GPU) → complete / fail`. On completion the provider is paid its cost
minus the protocol fee plus its reputation bonus, the GPU frees, and the job's speed and quality feed
straight back into the provider's reputation.

## Task catalog & pricing

| Task | Compute units | Baseline runtime |
|---|---|---|
| inference | 1.0 | 4s |
| automation | 1.5 | 8s |
| analysis | 2.0 | 10s |
| market | 2.5 | 12s |
| generation | 4.0 | 20s |

`cost = compute_units × per-unit baseline × demand multiplier`, in SOL. Demand rises with network
utilization.

## Agent execution layer

AI agents open a **budget session** (prepaid SOL), then autonomously chain jobs against it — request
GPU power, pay, receive output, continue — until the budget is exhausted. This makes Nunabot a
programmable execution backend for autonomous workflows.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/market` | network stats, utilization, SOL price |
| GET | `/api/catalog` | task types + live SOL cost |
| POST | `/api/bot/quote` · `/bot/request` | price a task / NL → priced task |
| POST | `/api/job/submit` | route + run a job |
| POST | `/api/job/<id>/complete` · `/fail` | close a job |
| GET | `/api/job/<id>` · `/job/list` | job status |
| POST | `/api/provider/register` | register GPUs |
| GET | `/api/providers?ranked=1` | reputation leaderboard |
| POST | `/api/provider/<id>/heartbeat` | uptime signal |
| POST | `/api/agent/session` · `/agent/<id>/run` | agent budget sessions |

## Run it

```bash
# backend
cd backend
pip install -r requirements.txt
python run.py            # :5001

# frontend
cd frontend
npm install
npm run dev              # :3000

# tests (no API keys / network — SOL price mocked)
pytest tests/ -v

# end-to-end walkthrough
python backend/scripts/simulate.py
```

Configuration is environment-driven; copy `.env.example` to `.env`. The bot task planner needs
`NUNA_LLM_API_KEY`; everything else runs without it.

## License

MIT — see [LICENSE](LICENSE).
