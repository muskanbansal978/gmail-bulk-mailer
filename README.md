# Gmail Bulk Mailer

Sends **50 job application emails per day** (Mon–Sat), distributed across 9:30 AM–2:18 PM IST in 5 chunks of 10. Runs automatically via **GitHub Actions** — no machine needs to be on. Attaches your resume, personalises each email with the recipient's name and job role, self-notifies after each chunk, and alerts you when the full list is exhausted.

---

## How it works

- GitHub Actions triggers the script **5 times a day**, Mon–Sat
- Each run sends **10 emails** → 50 total per day
- Progress is saved in `mailer_state.json` (committed back to the repo after each run)
- Emails are read from an Excel file with columns: `Email`, `Author`, `Role Title`
- Your resume PDF is attached to every email
- Helper files (Excel + resume) live in a **separate private repo** and are fetched at runtime — never exposed in this repo

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

### 1. Create this repo (gmail-bulk-mailer)

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/gmail-bulk-mailer.git
git branch -M main
git push -u origin main
```

> Make the repo **private**.

---

### 2. Create a separate private repo for Helper Files

Go to [github.com/new](https://github.com/new) → name `gmail-mailer-assets` → **Private** → no README → Create

Then push your Excel and resume there:

```bash
cd Helper_Files
git init
git add .
git commit -m "initial"
git remote add origin https://github.com/YOUR_USERNAME/gmail-mailer-assets.git
git branch -M main
git push -u origin main
```

Your Excel file must have these columns: `Email`, `Author`, `Role Title`

---

### 3. Generate a Gmail App Password

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Search **"App passwords"** → create one → copy the 16-character code

---

### 4. Create a Personal Access Token (PAT)

This lets the workflow fetch files from `gmail-mailer-assets` at runtime.

1. GitHub → profile **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **Generate new token**
3. Name: `mailer-assets-access`, Expiration: 1 year, Scope: check only `repo`
4. Copy the token

---

### 5. Add secrets to gmail-bulk-mailer

Go to `gmail-bulk-mailer` repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value |
|---|---|
| `GMAIL_USER` | your Gmail address |
| `GMAIL_APP_PASS` | the App Password from step 3 |
| `EXCEL_FILE` | `Helper_Files/your_list.xlsx` |
| `RESUME_PATH` | `Helper_Files/Your_Resume.pdf` |
| `ASSETS_PAT` | the PAT from step 4 |
| `ASSETS_REPO` | `YOUR_USERNAME/gmail-mailer-assets` |

---

### 6. Test before going live

```bash
pip install -r requirements.txt
python dry_run.py
```

Fix any ❌ errors shown. It verifies credentials, Excel columns, resume path, and previews the email.

---

### 7. Trigger a manual test run

Go to `gmail-bulk-mailer` → **Actions → Gmail Bulk Mailer → Run workflow**

Check that 10 emails are sent and `mailer_state.json` is committed back automatically.

---

## Updating Helper Files

When your mailing list or resume changes:

```bash
cd /path/to/Helper_Files
git add .
git commit -m "update mailing list"
git push
```

The next scheduled run picks up the latest files automatically. No secrets to update.

---

## Resetting for a new mailing list

1. Push the new Excel file to `gmail-mailer-assets`
2. Update `EXCEL_FILE` secret if the filename changed
3. Delete `mailer_state.json` from the `gmail-bulk-mailer` repo (or set `next_index` and `total_sent` to `0`)
4. The next scheduled run picks up from row 1

---

## Files

| File | Purpose |
|---|---|
| `email_scheduler.py` | Core script — sends one chunk of emails per run |
| `config.py` | All settings — reads from environment variables |
| `dry_run.py` | Validates setup without sending real emails |
| `.github/workflows/mailer.yml` | GitHub Actions schedule |
| `mailer_state.json` | Auto-created — tracks send progress |
| `mailer.log` | Auto-created — full send log |
