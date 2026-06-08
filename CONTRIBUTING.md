# Contributing to Nunabot

PRs welcome.

## Setup
```bash
git clone https://github.com/nunabot/nunabot.git
cd nunabot && cp .env.example .env
npm run setup
```

## Tests
```bash
pytest tests/ -v
```
Fully unit-tested with no API keys or network (SOL price mocked). Reputation, routing, the job
lifecycle, pricing, and the agent layer are all covered.

## Branches
`feature/`, `hotfix/`, `chore/`

## Commits
Conventional: `feat:`, `fix:`, `chore:`, `docs:`

## Roadmap
- Real GPU worker daemon (job pickup, sandboxed execution, signed heartbeats)
- On-chain SOL escrow + settlement program (Anchor)
- Verifiable execution proofs for output quality
- Slashing for failed/forged jobs tied to reputation
- Agent SDK for autonomous job chaining and callbacks
- Spot vs reserved capacity and per-task-type provider specialization

## Note on git
Commits are authored anonymously as the project — no personal contributor identity.
