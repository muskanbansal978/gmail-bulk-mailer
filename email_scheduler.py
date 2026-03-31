"""
Gmail Bulk Email Scheduler
- Reads emails from Excel sheet
- Distributes 50 emails daily from 9:30 AM to 3:30 PM IST (~7 min apart)
- Tracks progress via a state JSON file
- Sends self-notification after each batch
- Sends "all done" alert when list is exhausted
"""

import json
import time
import smtplib
import logging
import pandas as pd
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from config import (
    GMAIL_USER, GMAIL_APP_PASS,
    EXCEL_FILE, EMAIL_COL, NAME_COL, ROLE_COL, RESUME_PATH,
    BATCH_SIZE, CHUNK_SIZE, STATE_FILE,
    SUBJECT, BODY_TEMPLATE,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler("mailer.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ── State helpers ─────────────────────────────

def load_state() -> dict:
    if Path(STATE_FILE).exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"next_index": 0, "day": 1, "total_sent": 0}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ── Email helpers ─────────────────────────────

def send_email(to: str, subject: str, body: str, attach_resume: bool = False):
    msg = MIMEMultipart()
    msg["From"]    = GMAIL_USER
    msg["To"]      = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attach_resume and Path(RESUME_PATH).exists():
        with open(RESUME_PATH, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={Path(RESUME_PATH).name}",
        )
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.sendmail(GMAIL_USER, to, msg.as_string())


def send_batch_notification(day: int, sent_count: int, batch_emails: list[str], total_sent: int):
    subject = f"✅ Day {day} — {sent_count} emails sent"
    body = (
        f"Daily batch complete!\n\n"
        f"Day:          {day}\n"
        f"Sent today:   {sent_count}\n"
        f"Total so far: {total_sent}\n\n"
        f"Recipients:\n" + "\n".join(f"  • {e}" for e in batch_emails)
    )
    send_email(GMAIL_USER, subject, body)
    log.info("Batch notification sent to %s", GMAIL_USER)


def send_completion_notification(total_sent: int):
    subject = "🎉 Mailing list complete — import a new list!"
    body = (
        f"All emails have been sent!\n\n"
        f"Total sent: {total_sent}\n\n"
        f"The current mailing list ({EXCEL_FILE}) has been fully processed.\n"
        f"Please import a new Excel file and reset the state to start a fresh campaign.\n\n"
        f"Steps to reset:\n"
        f"  1. Replace '{EXCEL_FILE}' with your new mailing list.\n"
        f"  2. Delete '{STATE_FILE}'  (or set next_index to 0).\n"
        f"  3. The scheduler will pick up automatically at the next 9:30 AM run.\n"
    )
    send_email(GMAIL_USER, subject, body)
    log.info("Completion notification sent — all emails exhausted.")


# ── Core batch job ────────────────────────────

def run_batch():
    log.info("=== Batch job started ===")

    # Load Excel
    if not Path(EXCEL_FILE).exists():
        log.error("Excel file '%s' not found. Skipping.", EXCEL_FILE)
        return

    df = pd.read_excel(EXCEL_FILE)
    if EMAIL_COL not in df.columns:
        log.error("Column '%s' not found in Excel. Available: %s", EMAIL_COL, list(df.columns))
        return

    df = df.dropna(subset=[EMAIL_COL])
    all_emails = df[EMAIL_COL].str.strip().tolist()
    all_names  = (
        df[NAME_COL].fillna("there").tolist()
        if NAME_COL in df.columns
        else ["there"] * len(all_emails)
    )
    all_roles  = (
        df[ROLE_COL].fillna("the open role").tolist()
        if ROLE_COL in df.columns
        else ["the open role"] * len(all_emails)
    )

    state = load_state()
    start = state["next_index"]

    if start >= len(all_emails):
        log.info("All emails already sent. Waiting for new list.")
        send_completion_notification(state["total_sent"])
        return

    # Slice one chunk (GitHub Actions runs this script 5× per day)
    end          = min(start + CHUNK_SIZE, len(all_emails))
    batch_emails = all_emails[start:end]
    batch_names  = all_names[start:end]
    batch_roles  = all_roles[start:end]

    log.info("Sending chunk of %d emails (index %d → %d)", len(batch_emails), start, end)

    sent_this_batch  = 0
    failed_this_batch = 0
    sent_addresses   = []

    for i, (email, name, role) in enumerate(zip(batch_emails, batch_names, batch_roles)):
        try:
            subject = SUBJECT.format(role=role)
            body = BODY_TEMPLATE.format(name=name, role=role)
            send_email(email, subject, body, attach_resume=True)
            sent_addresses.append(email)
            sent_this_batch += 1
            log.info("Sent [%d/%d] → %s", i + 1, len(batch_emails), email)
            time.sleep(5)   # small gap to avoid Gmail rate limits
        except Exception as exc:
            log.error("Failed → %s | %s", email, exc)
            failed_this_batch += 1

    # Update state
    state["next_index"]  = end
    state["total_sent"] += sent_this_batch
    # Increment day only after a full batch (BATCH_SIZE emails) has been sent
    if end % BATCH_SIZE == 0 or end >= len(all_emails):
        state["day"] += 1
    save_state(state)

    log.info("Batch done. Sent=%d  Failed=%d  Next index=%d", sent_this_batch, failed_this_batch, end)

    # Self-notification
    try:
        send_batch_notification(state["day"] - 1, sent_this_batch, sent_addresses, state["total_sent"])
    except Exception as exc:
        log.error("Could not send batch notification: %s", exc)

    # Check if list is now exhausted
    if end >= len(all_emails):
        log.info("Entire mailing list processed!")
        try:
            send_completion_notification(state["total_sent"])
        except Exception as exc:
            log.error("Could not send completion notification: %s", exc)


if __name__ == "__main__":
    run_batch()
