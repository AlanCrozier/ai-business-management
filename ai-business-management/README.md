# LUMON Analytics

> **Predictive Insights for Customer Lifetime Value, Revenue, Employee Contribution & Profit**

An AI-powered Business Management & Enterprise Analytics Dashboard built with **FastAPI** (Python) and **Vite + React 19** (TypeScript). It loads pre-trained ML models to deliver real-time predictions and provides a comprehensive Enterprise Health Report. The system features multi-tenant data segmentation via Firebase Auth and Google Sheets API integration.

---

## Features

- **4 AI Prediction Engines** — CLV, Revenue, Employee Performance, Profit
- **Executive Dashboard** — Combined KPI cards, trend charts (Chart.js), interactive dashboard
- **Enterprise Health Report** — Scores, risk assessment, AI recommendations
- **Firebase Authentication** — Secure user login and multi-tenant data segmentation
- **Google Sheets Integration** — Connect and sync your own Google Sheets via encrypted service accounts
- **MySQL Database** — High-performance relational database via SQLAlchemy
- **Modern UI/UX** — Premium animations using Motion, styled with Tailwind CSS v4

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, MySQL, joblib |
| Frontend | Vite, React 19, TypeScript, Tailwind CSS v4, Chart.js, Motion |
| Authentication | Firebase Auth |
| Data Source | Google Sheets API (Service Accounts) |
| ML | scikit-learn RandomForestRegressor (.pkl models) |

---

## Project Structure

```
ai-business-management/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── database.py             # SQLAlchemy + MySQL config
│   ├── models/                 # ORM models (prediction, user, dataset)
│   ├── schemas/                # Pydantic v2 schemas
│   ├── services/               # ML service, Sheets Sync, Data Generator
│   ├── routers/                # API endpoints (predict, dashboard, sheets, accounts)
│   ├── train_revenue_model.py  # Model training scripts
│   └── requirements.txt
├── nexus-analytics/            # Vite + React Frontend
│   └── src/
│       ├── pages/              # React pages (Dashboard, Auth, etc.)
│       ├── components/         # Shared UI components
│       └── ...
├── models/                     # Pre-trained .pkl files
│   ├── clv_model.pkl
│   ├── revenue_model.pkl
│   ├── employee_model.pkl
│   └── profit_model.joblib
├── ARCHITECTURE.md             # System architecture & data workflow
└── README.md
```

---

## Quick Start

### 1. Backend

1. Install MySQL and create a database named `Lumon`.
2. Configure your `.env` or `database.py` with your MySQL connection string.

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 2. Frontend

1. Ensure you have your Firebase config in your environment variables.

```bash
cd nexus-analytics
npm install
npm run dev
```

Open: `http://localhost:5173` (or the port specified by Vite)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict/clv` | Customer Lifetime Value |
| POST | `/api/predict/revenue` | Revenue Forecast |
| POST | `/api/predict/employee` | Employee Performance |
| POST | `/api/predict/profit` | Profit Projection |
| POST | `/api/dashboard/summary` | Executive Dashboard KPIs |
| POST | `/api/sheets/sync` | Sync data from connected Google Sheet |
| POST | `/api/accounts/service-account`| Register/Update Google Sheets Service Account |
| GET | `/health` | API Health Check |

---

## Models

| Model | Algorithm | Features | Target |
|-------|-----------|----------|--------|
| CLV | RandomForest | age, gender, city, total_spent, membership, years, purchases | lifetime_value |
| Revenue | RandomForest | units_sold, region, month, day_of_week | revenue |
| Employee | RandomForest | age, years, attendance, training, promotions, tasks, ratings, salary | performance_score |
| Profit | RandomForest | operational_cost, marketing_cost, revenue | profit |

---

## License

MIT