"""Turn incoming files (e-mail, PDF, fax image, plain text) into message records."""

from __future__ import annotations

import email
import email.policy
import email.utils
import io
import re
import uuid
from datetime import datetime

OCR_LANGS = "deu+fra+ita+eng"


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def from_eml(data: bytes) -> dict:
    msg = email.message_from_bytes(data, policy=email.policy.default)
    body_part = msg.get_body(preferencelist=("plain", "html"))
    body = body_part.get_content() if body_part else ""
    if body_part is not None and body_part.get_content_type() == "text/html":
        body = re.sub(r"<[^>]+>", " ", body)
    attachments = []
    for part in msg.iter_attachments():
        name = part.get_filename() or "attachment"
        payload = part.get_payload(decode=True) or b""
        if name.lower().endswith(".pdf"):
            text = pdf_text(payload)
            if text.strip():
                attachments.append(f"[Attachment {name}]\n{text}")
    received = None
    if msg.get("Date"):
        try:
            received = (
                email.utils.parsedate_to_datetime(msg["Date"])
                .replace(tzinfo=None)
                .isoformat(timespec="minutes")
            )
        except (TypeError, ValueError):
            received = None
    if attachments:
        body = body.rstrip() + "\n\n" + "\n\n".join(attachments)
    return {
        "message_id": _new_id("eml"),
        "channel": "email",
        "sender": str(msg.get("From") or ""),
        "subject": str(msg.get("Subject") or ""),
        "body": body.strip(),
        "received_at": received,
    }


def pdf_text(data: bytes) -> str:
    import pdfplumber

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        text = "\n".join((page.extract_text() or "") for page in pdf.pages)
    if text.strip():
        return text
    import pypdfium2

    pages = pypdfium2.PdfDocument(data)
    return "\n".join(ocr_image(page.render(scale=2).to_pil()) for page in pages)


def ocr_image(img) -> str:
    import pytesseract

    return pytesseract.image_to_string(img.convert("L"), lang=OCR_LANGS)


def from_fax(data: bytes, filename: str) -> dict:
    if filename.lower().endswith(".pdf"):
        text = pdf_text(data)
    else:
        from PIL import Image

        text = ocr_image(Image.open(io.BytesIO(data)))
    lines = [line for line in text.splitlines() if line.strip()]
    subject = next(
        (
            line.strip()
            for line in lines[:8]
            if line.strip().isupper() and len(line.strip()) > 6
        ),
        lines[0] if lines else "",
    )
    return {
        "message_id": _new_id("fax"),
        "channel": "fax",
        "sender": "Fax",
        "subject": subject,
        "body": text.strip(),
        "received_at": datetime.now().isoformat(timespec="minutes"),
    }


def from_text(
    text: str, subject: str = "", sender: str = "", channel: str = "web_form"
) -> dict:
    return {
        "message_id": _new_id("txt"),
        "channel": channel,
        "sender": sender,
        "subject": subject,
        "body": text.strip(),
        "received_at": datetime.now().isoformat(timespec="minutes"),
    }


def from_upload(data: bytes, filename: str) -> dict:
    name = filename.lower()
    if name.endswith(".eml"):
        return from_eml(data)
    if name.endswith((".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff")):
        return from_fax(data, filename)
    return from_text(data.decode("utf-8", errors="replace"), subject=filename)
