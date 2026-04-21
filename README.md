# HR Case Insights

A drag-and-drop ServiceNow analytics dashboard built with FastAPI + a static frontend.

## Features

- Upload `.csv`, `.xlsx`, or `.xls` exports
- Executive summary metrics and insights
- Performance breakdown (state, priority, trend chart)
- Root-cause topic classification
- Filterable case table for quick drill-down

## Project structure

```text
hr-insights-app/
├── main.py              # FastAPI app
├── requirements.txt
├── render.yaml          # Render blueprint config
├── .gitignore
├── static/
│   └── index.html       # Full frontend (HTML/CSS/JS)
└── README.md
```

## Run locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the server:

```bash
uvicorn main:app --reload
```

3. Open [http://localhost:8000](http://localhost:8000)

## Deploy to Render

This repo includes `render.yaml`, so deployment is straightforward.

1. Push this project to GitHub
2. In Render, click **New** -> **Blueprint**
3. Select your repository
4. Render reads `render.yaml` and creates the web service

If you deploy manually as a Web Service instead of Blueprint:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Environment variables

No environment variables are required for the current UI.

Optional SMTP variables can still be configured if you use the backend email endpoint directly:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASS`
- `SENDER_EMAIL`

## API endpoints

- `GET /` - Serves the dashboard
- `POST /send-report` - Optional backend email endpoint
- `GET /health` - Service health check
