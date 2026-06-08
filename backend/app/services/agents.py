from dataclasses import dataclass, field
from ..config import Config
from ..utils import get_logger, new_id, utcnow_iso

log = get_logger("agents")


@dataclass
class AgentSession:
    """A programmable execution context for an autonomous AI agent. The agent
    opens a session with a prepaid SOL budget, then chains GPU jobs against it —
    each job draws from the budget until it's exhausted."""
    id: str
    agent: str
    budget_sol: float
    spent_sol: float = 0.0
    job_ids: list = field(default_factory=list)
    status: str = "open"          # open | closed
    created_at: str = ""

    @property
    def remaining_sol(self) -> float:
        return max(0.0, self.budget_sol - self.spent_sol)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent": self.agent,
            "budget_sol": round(self.budget_sol, 6),
            "spent_sol": round(self.spent_sol, 6),
            "remaining_sol": round(self.remaining_sol, 6),
            "jobs": len(self.job_ids),
            "job_ids": self.job_ids,
            "status": self.status,
            "created_at": self.created_at,
        }


_sessions: dict[str, AgentSession] = {}


class AgentLayer:
    """Lets AI agents request GPU power, pay from a session budget, receive
    outputs, and continue their workflow autonomously."""

    def __init__(self, job_engine, config=Config):
        self.jobs = job_engine
        self.config = config

    def open_session(self, agent: str, budget_sol: float) -> AgentSession:
        if budget_sol <= 0:
            raise ValueError("budget must be positive")
        s = AgentSession(id=new_id("sess"), agent=agent, budget_sol=budget_sol,
                         created_at=utcnow_iso())
        _sessions[s.id] = s
        return s

    def get_session(self, session_id: str) -> AgentSession:
        s = _sessions.get(session_id)
        if not s:
            raise ValueError(f"session not found: {session_id}")
        return s

    def run(self, session_id: str, task_key: str, units_multiple: float = 1.0,
            quality: float = 0.9) -> dict:
        """Run one job inside the session: price it, ensure budget, submit,
        complete, and debit the budget. Returns the job result + session state."""
        s = self.get_session(session_id)
        if s.status != "open":
            raise ValueError("session is closed")
        q = self.jobs.quote(task_key, units_multiple)
        if q.sol_cost > s.remaining_sol + 1e-12:
            raise ValueError(
                f"job costs {q.sol_cost:.6f} SOL but only {s.remaining_sol:.6f} SOL left in session"
            )
        job = self.jobs.submit(s.agent, task_key, units_multiple)
        self.jobs.complete(job.id, quality=quality)
        s.spent_sol += job.sol_cost
        s.job_ids.append(job.id)
        log.info("agent %s ran %s in session %s (%.6f SOL, %.6f left)",
                 s.agent, task_key, session_id, job.sol_cost, s.remaining_sol)
        return {"job": self.jobs.get(job.id).to_dict(), "session": s.to_dict()}

    def close_session(self, session_id: str) -> AgentSession:
        s = self.get_session(session_id)
        s.status = "closed"
        return s

    def list_sessions(self, agent: str = None) -> list[AgentSession]:
        sessions = list(_sessions.values())
        if agent:
            sessions = [x for x in sessions if x.agent == agent]
        return sessions
