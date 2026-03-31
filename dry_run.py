"""
Dry-run tester — validates your Excel file and config WITHOUT sending real emails.
Run this first to confirm everything is wired up correctly.
"""

import json
import pandas as pd
from pathlib import Path
from config import (
    EXCEL_FILE, EMAIL_COL, NAME_COL, ROLE_COL, RESUME_PATH,
    BATCH_SIZE, STATE_FILE,
    GMAIL_USER, GMAIL_APP_PASS, SELF_EMAIL, SUBJECT, BODY_TEMPLATE,
)

print("=" * 55)
print("  Gmail Bulk Mailer — Dry Run Checker")
print("=" * 55)

# 1. Config check
print("\n[1] Config")
print(f"  Sender      : {GMAIL_USER}")
print(f"  Self notify : {SELF_EMAIL}")
print(f"  Batch size  : {BATCH_SIZE}")
print(f"  Excel file  : {EXCEL_FILE}")
print(f"  Resume      : {RESUME_PATH}")
print(f"  State file  : {STATE_FILE}")
masked = GMAIL_APP_PASS[:4] + "****" if len(GMAIL_APP_PASS) > 4 else "NOT SET"
print(f"  App password: {masked}")

# 2. Excel check
print("\n[2] Excel file")
if not Path(EXCEL_FILE).exists():
    print(f"  ❌  File not found: {EXCEL_FILE}")
else:
    df = pd.read_excel(EXCEL_FILE)
    print(f"  ✅  Loaded. Columns: {list(df.columns)}")
    print(f"      Total rows       : {len(df)}")
    missing = [c for c in [EMAIL_COL, NAME_COL, ROLE_COL] if c not in df.columns]
    if missing:
        print(f"  ❌  Missing columns: {missing}")
    else:
        valid = df[EMAIL_COL].dropna()
        print(f"      Valid emails     : {len(valid)}")
        batches = -(-len(valid) // BATCH_SIZE)   # ceiling division
        print(f"      Batches needed   : {batches} days")
        print(f"      Preview (first 5):")
        for _, row in df.head(5).iterrows():
            print(f"        • {row[EMAIL_COL]}  |  {row[NAME_COL]}  |  {row[ROLE_COL]}")

# 3. State check
print("\n[3] State file")
if Path(STATE_FILE).exists():
    with open(STATE_FILE) as f:
        state = json.load(f)
    print(f"  Found state: {state}")
    print(f"  Next email index : {state['next_index']}")
    print(f"  Emails sent so far: {state['total_sent']}")
else:
    print("  No state file — fresh start (index=0)")

# 4. Resume check
print("\n[4] Resume")
if Path(RESUME_PATH).exists():
    size_kb = Path(RESUME_PATH).stat().st_size // 1024
    print(f"  ✅  Found: {RESUME_PATH} ({size_kb} KB)")
else:
    print(f"  ❌  Resume not found: {RESUME_PATH}")

# 5. Email template preview
print("\n[5] Email preview")
sample_role = "AI/ML Engineer"
print(f"  Subject : {SUBJECT.format(role=sample_role)}")
body_sample = BODY_TEMPLATE.format(name="Yashika", role=sample_role)
print("  Body:\n" + "\n".join(f"    {l}" for l in body_sample.splitlines()))

# 6. SMTP connectivity (optional, skipped in true dry-run)
print("\n[6] SMTP connection")
try:
    import smtplib
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as s:
        s.login(GMAIL_USER, GMAIL_APP_PASS)
    print("  ✅  Login successful — credentials are valid!")
except Exception as e:
    print(f"  ❌  SMTP login failed: {e}")
    print("      Make sure 2-FA is on and you're using an App Password.")

print("\n" + "=" * 55)
print("  Dry run complete. Fix any ❌ above, then run:")
print("  python email_scheduler.py")
print("=" * 55)
