import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.providers import ProviderRegistry, _providers
from app.services.router import JobRouter
from app.config import Config


def setup_function():
    _providers.clear()


def make():
    reg = ProviderRegistry(Config)
    return reg, JobRouter(reg, Config)


def test_no_capacity_raises():
    reg, router = make()
    p = reg.register("a", 1)
    p.busy = 1
    try:
        router.pick()
        assert False
    except ValueError:
        pass


def test_reputation_wins_routing():
    reg, router = make()
    good = reg.register("good", 4)
    bad = reg.register("bad", 4)
    for _ in range(30):
        reg.heartbeat(good.id, online=True)
        reg.record_result(good.id, success=True, speed_ratio=0.7, quality=0.95)
        reg.heartbeat(bad.id, online=False)
        reg.record_result(bad.id, success=False)
    assert router.pick().id == good.id


def test_only_available_providers_considered():
    reg, router = make()
    good = reg.register("good", 2)
    other = reg.register("other", 2)
    for _ in range(20):
        reg.heartbeat(good.id, online=True)
        reg.record_result(good.id, success=True, speed_ratio=0.7, quality=0.95)
    good.busy = good.gpus  # fully booked
    # even though 'good' has higher rep, it has no capacity → other wins
    assert router.pick().id == other.id


def test_ranked_orders_by_score():
    reg, router = make()
    a = reg.register("a", 4)
    b = reg.register("b", 4)
    for _ in range(20):
        reg.heartbeat(a.id, online=True)
        reg.record_result(a.id, success=True, speed_ratio=0.7, quality=0.95)
    ranked = router.ranked()
    assert ranked[0].id == a.id
