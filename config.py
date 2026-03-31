# ─────────────────────────────────────────────
#  CONFIG — edit these values
# ─────────────────────────────────────────────
import os

GMAIL_USER     = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASS", "")

EXCEL_FILE     = os.environ.get("EXCEL_FILE", "")
RESUME_PATH    = os.environ.get("RESUME_PATH", "")

EMAIL_COL      = "Email"
NAME_COL       = "Author"
ROLE_COL       = "Role Title"

BATCH_SIZE     = 50                           # Total emails per day
CHUNK_SIZE     = 10                           # Emails per scheduled run (5 runs × 10 = 50)
STATE_FILE     = "mailer_state.json"          # Tracks progress across runs

# Email content
SUBJECT        = "Application for {role} — Muskan Bansal"
BODY_TEMPLATE  = """\
Hi {name},

I hope this message finds you well. I came across the {role} opportunity and wanted to reach out to express my interest.

I have hands-on experience in AI/ML and data science — spanning model development, deployment, and working with large-scale datasets. I am confident my background aligns well with what you are looking for.

I have attached my resume for your review. I would love the opportunity to connect and discuss how I can contribute to your team.

Looking forward to hearing from you.

Best regards,
Muskan Bansal
muskanbansal978@gmail.com
"""
# ─────────────────────────────────────────────
