"""Read new messages from an IMAP mailbox (practice mail server, HIN mail via an IMAP bridge).

Read-only by default: messages are fetched with BODY.PEEK and never deleted or moved.
"""

from __future__ import annotations

import imaplib
import os
from dataclasses import dataclass, field
from email.utils import parseaddr

from . import ingest


@dataclass
class ImapConfig:
    host: str
    user: str
    password: str = field(repr=False)
    port: int = 993
    security: str = "ssl"  # ssl | starttls | plain
    folder: str = "INBOX"
    unseen_only: bool = True
    mark_seen: bool = False
    limit: int | None = None

    @classmethod
    def from_env(cls) -> "ImapConfig | None":
        host = os.getenv("INBREV_IMAP_HOST")
        if not host:
            return None
        security = os.getenv("INBREV_IMAP_SECURITY", "ssl")
        return cls(
            host=host,
            user=os.getenv("INBREV_IMAP_USER", ""),
            password=os.getenv("INBREV_IMAP_PASSWORD", ""),
            port=int(
                os.getenv("INBREV_IMAP_PORT") or ("993" if security == "ssl" else "143")
            ),
            security=security,
            folder=os.getenv("INBREV_IMAP_FOLDER", "INBOX"),
        )


def connect(cfg: ImapConfig) -> imaplib.IMAP4:
    if cfg.security == "ssl":
        conn = imaplib.IMAP4_SSL(cfg.host, cfg.port, timeout=30)
    else:
        conn = imaplib.IMAP4(cfg.host, cfg.port, timeout=30)
        if cfg.security == "starttls":
            conn.starttls()
        elif cfg.security != "plain":
            raise ValueError(f"unknown IMAP security {cfg.security!r}")
    conn.login(cfg.user, cfg.password)
    return conn


def channel_for(sender: str) -> str:
    domain = parseaddr(sender)[1].rpartition("@")[2].lower()
    return "hin_mail" if "hin" in domain.split(".") else "email"


def fetch(cfg: ImapConfig, conn: imaplib.IMAP4 | None = None) -> list[dict]:
    """Return new messages as Inbrev message records (oldest first)."""
    own = conn is None
    conn = conn or connect(cfg)
    try:
        status, _ = conn.select(cfg.folder, readonly=not cfg.mark_seen)
        if status != "OK":
            raise RuntimeError(f"cannot open folder {cfg.folder!r}")
        status, data = conn.uid("SEARCH", None, "UNSEEN" if cfg.unseen_only else "ALL")
        if status != "OK":
            raise RuntimeError("IMAP search failed")
        uids = (data[0] or b"").split()
        if cfg.limit:
            uids = uids[: cfg.limit]
        out = []
        for uid in uids:
            status, parts = conn.uid("FETCH", uid, "(BODY.PEEK[])")
            raw = next((p[1] for p in parts or [] if isinstance(p, tuple)), None)
            if status != "OK" or raw is None:
                continue
            m = ingest.from_eml(raw)
            m["message_id"] = f"imap-{uid.decode()}"
            m["channel"] = channel_for(m["sender"])
            out.append(m)
            if cfg.mark_seen:
                conn.uid("STORE", uid, "+FLAGS", r"(\Seen)")
        return out
    finally:
        if own:
            try:
                conn.logout()
            except (imaplib.IMAP4.error, OSError):
                pass
