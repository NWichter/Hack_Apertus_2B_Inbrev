from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(os.getenv("INBREV_HOME", Path(__file__).resolve().parents[2]))
REPO_DATA = PROJECT_ROOT / "data"


def load_dotenv(path: Path) -> None:
    """Minimal .env reader; existing environment variables win."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class Settings:
    llm_name: str = field(
        default_factory=lambda: os.getenv("LLM_NAME", "apertus-v1.5-8b")
    )
    llm_base_url: str = field(
        default_factory=lambda: os.getenv(
            "LLM_BASE_URL", "http://localhost:8080/v1"
        ).rstrip("/")
    )
    llm_api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", "none"))
    data_dir: Path = field(
        default_factory=lambda: Path(os.getenv("DATA_DIR", str(REPO_DATA)))
    )
    samples: int = field(default_factory=lambda: int(os.getenv("INBREV_SAMPLES", "3")))
    temperature: float = field(
        default_factory=lambda: float(os.getenv("INBREV_TEMPERATURE", "0.7"))
    )
    max_tokens: int = field(
        default_factory=lambda: int(os.getenv("INBREV_MAX_TOKENS", "900"))
    )
    concurrency: int = field(
        default_factory=lambda: int(os.getenv("INBREV_CONCURRENCY", "3"))
    )
    split_samples: str = field(
        default_factory=lambda: os.getenv("INBREV_SPLIT_SAMPLES", "auto").lower()
    )
    # Extra JSON merged into every chat request, e.g. to switch off reasoning of a comparison model.
    extra_body: str = field(default_factory=lambda: os.getenv("INBREV_EXTRA_BODY", ""))
    timeout: float = field(
        default_factory=lambda: float(os.getenv("INBREV_TIMEOUT", "180"))
    )
    audit_log: Path = field(
        default_factory=lambda: Path(
            os.getenv("INBREV_AUDIT_LOG", str(PROJECT_ROOT / "runs" / "audit.jsonl"))
        )
    )


def settings() -> Settings:
    return Settings()
