from dataclasses import dataclass


@dataclass
class TaskType:
    """A category of AI task the bot can run. compute_units approximates how
    much GPU work a 'standard' job of this type takes; est_seconds is the
    baseline runtime used to judge provider speed."""
    key: str
    label: str
    compute_units: float
    est_seconds: float

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "compute_units": self.compute_units,
            "est_seconds": self.est_seconds,
        }


_CATALOG: dict[str, TaskType] = {
    "inference":  TaskType("inference", "Model inference", 1.0, 4.0),
    "generation": TaskType("generation", "Image/video generation", 4.0, 20.0),
    "analysis":   TaskType("analysis", "Data analysis", 2.0, 10.0),
    "automation": TaskType("automation", "Workflow automation", 1.5, 8.0),
    "market":     TaskType("market", "Market processing", 2.5, 12.0),
}


class TaskCatalog:
    """Read-only registry of supported task types."""

    def get(self, key: str) -> TaskType:
        t = _CATALOG.get(key)
        if not t:
            raise ValueError(f"unknown task type: {key}")
        return t

    def is_supported(self, key: str) -> bool:
        return key in _CATALOG

    def list_all(self) -> list[TaskType]:
        return list(_CATALOG.values())
