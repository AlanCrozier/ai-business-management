# AI-Based Enterprise Analytics

> **Predictive Insights for Customer Lifetime Value, Revenue, Employee Contribution & Profit**

An AI-powered Business Management & Enterprise Analytics Dashboard built with **FastAPI** (Python) and **Next.js 15** (TypeScript). It loads 4 pre-trained ML models to deliver real-time predictions and a comprehensive Enterprise Health Report.

---

## Features

- **4 AI Prediction Engines** — CLV, Revenue, Employee Performance, Profit
- **Executive Dashboard** — Combined KPI cards, trend charts (Recharts), health radar
- **Enterprise Health Report** — Scores, risk assessment, AI recommendations
- **Prediction History** — All predictions saved to SQLite via SQLAlchemy
- **Dark Mode Default** — Premium glassmorphism UI with theme toggle
- **Responsive Design** — Collapsible sidebar, mobile-friendly layout

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, SQLite, joblib |
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, Recharts |
| UI | Lucide Icons, Sonner Toasts, next-themes |
| ML | scikit-learn RandomForestRegressor (.pkl models) |

---

## Project Structure

```
ai-business-management/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── database.py             # SQLAlchemy + SQLite
│   ├── models/prediction.py    # ORM model
│   ├── schemas/                # Pydantic v2 schemas
│   ├── services/ml_service.py  # Model loader + predictor
│   ├── routers/                # API endpoints
│   ├── train_revenue_model.py  # Revenue model training
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/                # Next.js App Router pages
│       ├── components/         # Shared UI components
│       └── lib/api.ts          # Backend API wrapper
├── models/                     # Pre-trained .pkl files
│   ├── clv_model.pkl
│   ├── revenue_model.pkl
│   ├── employee_model.pkl
│   └── profit_model.joblib
└── README.md
```

---

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict/clv` | Customer Lifetime Value |
| POST | `/api/predict/revenue` | Revenue Forecast |
| POST | `/api/predict/employee` | Employee Performance |
| POST | `/api/predict/profit` | Profit Projection |
| GET | `/api/predict/history` | Prediction History |
| POST | `/api/dashboard/summary` | Executive Dashboard KPIs |
| POST | `/api/dashboard/health-report` | Enterprise Health Report |
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