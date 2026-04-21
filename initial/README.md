# HR Case Insights

A drag-and-drop ServiceNow HR analytics tool with email reporting.

## Project structure

```
hr-insights-app/
├── main.py              ← FastAPI backend (email sending)
├── requirements.txt
├── .env                 ← Your SMTP credentials (never commit this)
├── static/
│   └── index.html       ← The full app (HTML/CSS/JS)
└── README.md
```

## Run locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure email

Edit `.env` with your SMTP credentials:

```env
# Gmail (recommended)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=you@gmail.com
SMTP_PASS=your_app_password   # NOT your Gmail password — see below

# NYU / Office 365
# SMTP_HOST=smtp.office365.com
# SMTP_PORT=587
# SMTP_USER=you@nyu.edu
# SMTP_PASS=your_password
```

**Gmail app password setup:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification if not already on
3. Go to https://myaccount.google.com/apppasswords
4. Create a new app password → copy the 16-character code into SMTP_PASS

### 3. Start the server

```bash
uvicorn main:app --reload
```

Open http://localhost:8000 in your browser.

---

## Deploy to Render (free tier)

1. Push this folder to a GitHub repo
2. Go to https://render.com → New Web Service → connect your repo
3. Set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render dashboard (same as your .env)
5. Deploy — you'll get a public URL like `https://hr-insights.onrender.com`

## Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```
Then add your env vars in the Railway dashboard.

---

## How email works

When a user clicks "Send report":
1. The browser collects the dashboard summary (metrics + topic breakdown) as HTML
2. It POSTs to `/send-report` on the FastAPI server
3. FastAPI builds a styled HTML email and optionally attaches the CSV
4. It sends via SMTP using your credentials in `.env`

The app **never stores** any uploaded data — everything is processed in the browser
and only the summary text is sent to the backend for emailing.

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serves the app |
| POST | `/send-report` | Sends the email report |
| GET | `/health` | Check if SMTP is configured |
