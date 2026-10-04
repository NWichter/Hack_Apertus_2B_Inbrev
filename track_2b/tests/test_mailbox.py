from email.message import EmailMessage

from inbrev import mailbox


def _eml(sender: str, subject: str, body: str) -> bytes:
    m = EmailMessage()
    m["From"], m["To"], m["Subject"] = sender, "praxis@praxis.example", subject
    m["Date"] = "Mon, 05 Oct 2026 08:15:00 +0200"
    m.set_content(body)
    return m.as_bytes()


class FakeImap:
    def __init__(self, mails: dict[bytes, bytes]):
        self.mails, self.calls = mails, []

    def select(self, folder, readonly=False):
        self.calls.append(("select", folder, readonly))
        return "OK", [b"2"]

    def uid(self, cmd, *args):
        self.calls.append((cmd, *args))
        if cmd == "SEARCH":
            return "OK", [b" ".join(self.mails)]
        if cmd == "FETCH":
            return "OK", [(b"1 (UID 1 BODY[] {100}", self.mails[args[0]]), b")"]
        return "OK", [b""]


def test_fetch_is_read_only_and_maps_messages():
    fake = FakeImap(
        {
            b"7": _eml("Labor <befunde@labor.hin.example>", "Befund", "Laborbefund für Herrn Muster."),
            b"9": _eml("anna@mail.example", "Termin", "Ich möchte meinen Termin verschieben."),
        }
    )
    cfg = mailbox.ImapConfig(host="x", user="u", password="p")
    msgs = mailbox.fetch(cfg, conn=fake)
    assert [m["message_id"] for m in msgs] == ["imap-7", "imap-9"]
    assert [m["channel"] for m in msgs] == ["hin_mail", "email"]
    assert msgs[1]["body"].startswith("Ich möchte") and msgs[1]["received_at"] == "2026-10-05T08:15"
    assert ("select", "INBOX", True) in fake.calls
    assert all(c[0] != "STORE" for c in fake.calls)
    assert any(c[0] == "SEARCH" and "UNSEEN" in c for c in fake.calls)
