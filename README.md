# Gmail Bulk Mailer

Sends **50 job application emails per day** (Mon–Sat), distributed across 9:30 AM–2:18 PM IST in 5 chunks of 10. Runs automatically via **GitHub Actions** — no machine needs to be on. Attaches your resume, personalises each email with the recipient's name and job role, self-notifies after each chunk, and alerts you when the full list is exhausted.

---

## How it works

- GitHub Actions triggers the script **5 times a day**, Mon–Sat
- Each run sends **10 emails** → 50 total per day
- Progress is saved in `mailer_state.json` (committed back to the repo after each run)
- Emails are read from an Excel file in `Helper_Files/` with columns: `Email`, `Author`, `Role Title`
- Your resume PDF from `Helper_Files/` is attached to every email

```
Run 1 — 09:30 IST → emails 1–10
Run 2 — 10:42 IST → emails 11–20
Run 3 — 11:54 IST → emails 21–30
Run 4 — 13:06 IST → emails 31–40
Run 5 — 14:18 IST → emails 41–50
(no runs on Sunday)
```

---

## Setup

### 1. Fork / clone this repo (make it private)

> Keep the repo **private** — it contains your mailing list and resume.

### 2. Add your files

Place the following in `Helper_Files/`:
- Your mailing list: `your_list.xlsx` with columns `Email`, `Author`, `Role Title`
- Your resume: `Your_Resume.pdf`

### 3. Add GitHub Secrets

Go to repo **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret | Value |
|---|---|
| `GMAIL_USER` | your Gmail address |
| `GMAIL_APP_PASS` | Gmail App Password (see below) |
| `EXCEL_FILE` | `Helper_Files/your_list.xlsx` |
| `RESUME_PATH` | `Helper_Files/Your_Resume.pdf` |

### 4. Generate a Gmail App Password

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Search **"App passwords"** → create one → copy the 16-character code
4. Use that as `GMAIL_APP_PASS`

### 5. Test before going live

```bash
pip install -r requirements.txt
python dry_run.py
```

Fix any ❌ errors shown. It verifies credentials, Excel columns, resume path, and previews the email.

### 6. Push to GitHub — it runs automatically

Once secrets are set and the repo is pushed, GitHub Actions handles everything. No terminal to keep open, no cron to configure.

---

## Resetting for a new mailing list

1. Replace the Excel file in `Helper_Files/`
2. Update the `EXCEL_FILE` secret if the filename changed
3. Delete `mailer_state.json` from the repo (or set `next_index` and `total_sent` to `0`)
4. The next scheduled run picks up from row 1

---

## Files

| File | Purpose |
|---|---|
| `email_scheduler.py` | Core script — sends one chunk of emails per run |
| `config.py` | All settings — reads from environment variables |
| `dry_run.py` | Validates setup without sending real emails |
| `Helper_Files/` | Your Excel mailing list and resume PDF |
| `.github/workflows/mailer.yml` | GitHub Actions schedule |
| `mailer_state.json` | Auto-created — tracks send progress |
| `mailer.log` | Auto-created — full send log |
