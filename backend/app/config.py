import os


class Config:
    """Central configuration. Environment-driven with safe defaults so the
    protocol runs end-to-end in dev without any keys (prices are mocked)."""

    # --- Protocol economics ---
    PROTOCOL_FEE_BPS = int(os.getenv("NUNA_FEE_BPS", "80"))            # 0.80% protocol fee
    DEMAND_PRICE_SLOPE = float(os.getenv("NUNA_DEMAND_SLOPE", "0.5"))  # price kicker per utilization
    COMPUTE_UNIT_USD = float(os.getenv("NUNA_CU_USD", "0.012"))       # $ per compute-unit baseline

    # --- Provider reputation weights (must sum to 1.0) ---
    REP_W_UPTIME = float(os.getenv("NUNA_RW_UPTIME", "0.25"))
    REP_W_SPEED = float(os.getenv("NUNA_RW_SPEED", "0.20"))
    REP_W_RELIABILITY = float(os.getenv("NUNA_RW_RELIABILITY", "0.30"))
    REP_W_VOLUME = float(os.getenv("NUNA_RW_VOLUME", "0.10"))
    REP_W_QUALITY = float(os.getenv("NUNA_RW_QUALITY", "0.15"))

    REP_MAX_SCORE = 1000
    # How much reputation tilts routing and earnings.
    ROUTING_REP_WEIGHT = float(os.getenv("NUNA_ROUTING_REP_WEIGHT", "0.7"))
    REP_MAX_EARNINGS_BONUS = float(os.getenv("NUNA_REP_EARN_BONUS", "0.10"))  # top reps net +10%

    # Speed reference: a job finishing at/under this ratio of its estimate is "fast"
    SPEED_TARGET_RATIO = float(os.getenv("NUNA_SPEED_TARGET", "1.0"))

    # --- LLM (bot task planner) ---
    LLM_PROVIDER = os.getenv("NUNA_LLM_PROVIDER", "anthropic")
    LLM_API_KEY = os.getenv("NUNA_LLM_API_KEY", "")
    LLM_MODEL = os.getenv("NUNA_LLM_MODEL", "claude-haiku-4-5-20251001")
    LLM_BASE_URL = os.getenv("NUNA_LLM_BASE_URL", "https://api.anthropic.com/v1")

    # --- Solana / price oracle ---
    SOLANA_RPC = os.getenv("NUNA_SOLANA_RPC", "https://api.mainnet-beta.solana.com")
    PRICE_API = os.getenv("NUNA_PRICE_API", "https://api.coingecko.com/api/v3")
    PRICE_CACHE_TTL = int(os.getenv("NUNA_PRICE_TTL", "30"))

    HOST = os.getenv("NUNA_HOST", "0.0.0.0")
    PORT = int(os.getenv("NUNA_PORT", "5001"))
    DEBUG = os.getenv("NUNA_DEBUG", "true").lower() == "true"

    @classmethod
    def validate(cls):
        total = (cls.REP_W_UPTIME + cls.REP_W_SPEED + cls.REP_W_RELIABILITY
                 + cls.REP_W_VOLUME + cls.REP_W_QUALITY)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Reputation weights must sum to 1.0, got {total}")
        if not cls.LLM_API_KEY:
            raise ValueError("NUNA_LLM_API_KEY is required for the bot task planner")
        return True
