import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.providers import ProviderRegistry, _providers
from app.config import Config


def setup_function():
    _providers.clear()


def test_register_provider():
    reg = ProviderRegistry(Config)
    p = reg.register("opA", 4)
    assert p.gpus == 4
    assert p.available == 4
    assert reg.reputation(p.id) >= 0


def test_register_rejects_zero_gpus():
    reg = ProviderRegistry(Config)
    try:
        reg.register("opA", 0)
        assert False
    except ValueError:
        pass


def test_uptime_raises_reputation():
    reg = ProviderRegistry(Config)
    a = reg.register("good", 2)
    b = reg.register("bad", 2)
    for _ in range(20):
        reg.heartbeat(a.id, online=True)
        reg.heartbeat(b.id, online=False)
    assert reg.reputation(a.id) > reg.reputation(b.id)


def test_reliability_matters():
    reg = ProviderRegistry(Config)
    a = reg.register("reliable", 2)
    b = reg.register("flaky", 2)
    for _ in range(10):
        reg.record_result(a.id, success=True, speed_ratio=0.9, quality=0.9)
        reg.record_result(b.id, success=False)
    assert reg.reputation(a.id) > reg.reputation(b.id)


def test_speed_component():
    reg = ProviderRegistry(Config)
    fast = reg.register("fast", 2)
    slow = reg.register("slow", 2)
    for _ in range(10):
        reg.record_result(fast.id, success=True, speed_ratio=0.6, quality=0.9)
        reg.record_result(slow.id, success=True, speed_ratio=2.0, quality=0.9)
    assert reg.components(fast.id)["speed"] > reg.components(slow.id)["speed"]


def test_quality_component():
    reg = ProviderRegistry(Config)
    hi = reg.register("hi", 2)
    lo = reg.register("lo", 2)
    for _ in range(10):
        reg.record_result(hi.id, success=True, speed_ratio=1.0, quality=0.98)
        reg.record_result(lo.id, success=True, speed_ratio=1.0, quality=0.5)
    assert reg.components(hi.id)["quality"] > reg.components(lo.id)["quality"]


def test_volume_grows_with_completed_jobs():
    reg = ProviderRegistry(Config)
    p = reg.register("busy", 2)
    before = reg.components(p.id)["volume"]
    for _ in range(50):
        reg.record_result(p.id, success=True, speed_ratio=1.0, quality=0.9)
    assert reg.components(p.id)["volume"] > before


def test_tiers_and_bonus_progress():
    reg = ProviderRegistry(Config)
    p = reg.register("elite", 4)
    for _ in range(60):
        reg.heartbeat(p.id, online=True)
        reg.record_result(p.id, success=True, speed_ratio=0.7, quality=0.97)
    assert reg.tier(p.id) in {"trusted", "elite"}
    assert 0 <= reg.earnings_bonus(p.id) <= Config.REP_MAX_EARNINGS_BONUS + 1e-9


def test_components_bounded():
    reg = ProviderRegistry(Config)
    p = reg.register("x", 2)
    reg.heartbeat(p.id, online=True)
    reg.record_result(p.id, success=True, speed_ratio=1.0, quality=0.8)
    comps = reg.components(p.id)
    assert set(comps) == {"uptime", "speed", "reliability", "volume", "quality"}
    assert all(0.0 <= v <= 1.0 for v in comps.values())
