# AI Business Management Platform (LUMON Analytics)

> **Predictive Insights for Customer Lifetime Value, Revenue, Employee Contribution & Profit**

Welcome to the **AI Business Management** repository. This project houses **LUMON Analytics**, an enterprise-grade, AI-powered Business Management & Enterprise Analytics Dashboard. It provides real-time predictive insights and a comprehensive Enterprise Health Report by leveraging pre-trained Machine Learning models.

## 🚀 Key Features

- **4 AI Prediction Engines** — Forecast Customer Lifetime Value (CLV), Revenue, Employee Performance, and overall Profit.
- **Executive Dashboard** — Combined KPI cards, dynamic trend charts (Chart.js), and interactive reporting.
- **Enterprise Health Report** — Get actionable scores, risk assessments, and AI-driven recommendations.
- **Secure Architecture** — Multi-tenant data segmentation powered by **Firebase Auth**.
- **Seamless Integrations** — Connect and synchronize your own **Google Sheets** via encrypted service accounts for live data.
- **Modern Tech Stack** — Built with a high-performance **FastAPI** (Python) backend and a sleek **Vite + React 19** frontend featuring **Tailwind CSS v4** and **Motion** animations.

---

## 🏗️ System Architecture

The platform follows a decoupled, secure, and highly scalable architecture:

1. **Presentation Layer (Frontend):** Located in `Lumon/nexus-analytics/`, the Vite + React frontend handles all visualizations, KPI rendering, and user interactions.
2. **Security & Auth:** Firebase issues secure UIDs used to strictly isolate data per tenant.
3. **API & Controller (Backend):** The `Lumon/backend/` FastAPI server acts as the central hub. It securely fetches user data from Google Sheets, processes it, and routes the traffic.
4. **AI Engine:** Pre-trained `scikit-learn` models (`.pkl` and `.joblib` in `Lumon/models/`) generate predictions on the fly based on the synced data.
5. **Database Layer:** 
   - **MySQL** manages internal state, configurations, and encrypted Service Account keys.
   - **Google Sheets** acts as the dynamic cloud database for raw business data and stores the AI predictions.

---

## 📂 Project Structure

```text
ai-business-management/
├── Lumon/
│   ├── backend/                 # FastAPI server, SQLAlchemy, API routers, and ML services
│   ├── nexus-analytics/         # Vite + React 19 Frontend application
│   ├── models/                  # Pre-trained ML models (RandomForestRegressor)
│   ├── ARCHITECTURE.md          # Detailed system architecture and data workflow
│   └── README.md                # Lumon-specific documentation
└── README.md                    # This file
```

---

## 🛠️ Quick Start Guide

Navigate into the `Lumon` directory to start up the services.

### 1. Start the Backend (FastAPI)
Requires Python 3.11+ and a running MySQL instance.

```bash
cd Lumon/backend
pip install -r requirements.txt
# Configure your .env or database.py with your MySQL credentials
uvicorn main:app --reload --port 8000
```
*API documentation will be available at `http://localhost:8000/docs`*

### 2. Start the Frontend (React + Vite)
Requires Node.js.

```bash
cd Lumon/nexus-analytics
npm install
npm run dev
```
*The web dashboard will be available at `http://localhost:5173`*

---

## 🧠 Machine Learning Models

The platform utilizes Random Forest algorithms to deliver predictive metrics:

| Model | Target | Key Features Used |
|-------|--------|-------------------|
| **CLV** | `lifetime_value` | age, gender, city, total_spent, membership, years, purchases |
| **Revenue** | `revenue` | units_sold, region, month, day_of_week |
| **Employee** | `performance_score` | age, years, attendance, training, promotions, tasks, ratings, salary |
| **Profit** | `profit` | operational_cost, marketing_cost, revenue |

---

For more detailed information, please refer to the detailed documentation inside the `Lumon/` directory.