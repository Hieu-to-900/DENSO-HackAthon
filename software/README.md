# DENSO BYTECO – Forecasting & Market Intelligence Suite

Hệ thống dự báo nhu cầu – rủi ro cung ứng – market intelligence – news agent – logistics dashboard cho DENSO APAC.

Toàn bộ kiến trúc gồm:  
1) Backend API (Flask)  
2) AI Workspace (Forecasting + Data Collector Agent)  
3) PostgreSQL Data Lake & Mart Layer qua Docker  
<br>

---
## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN
---


```text
Demand-Forecasting/software/
├─ docker-compose.yml
├─ requirements.txt
├─ README.md
├─ schema.sql
├─ seed_data.sql
├─ seed_alter_v3.sql
│
├─ backend/                              # Flask API Backend
│  ├─ run.py                             # Entry point: python run.py
│  ├─ README.md
│  │
│  └─ denso_app/                         # Main Flask Application
│     ├─ __init__.py                     # create_app(), register_blueprints()
│     ├─ config.py                       # Configuration: BaseConfig, DevConfig, ProdConfig
│     ├─ db.py                           # Database utilities: query_all, query_one, execute_sql
│     │
│     ├─ core/                           # Core utilities & constants
│     │  ├─ __init__.py
│     │  └─ constants.py                 # DENSO_SKUS, REGIONS, CHANNELS, etc.
│     │
│     ├─ api/                            # API Routes (Blueprint modules)
│     │  ├─ __init__.py                  # Blueprint registration
│     │  ├─ dashboard.py                 # GET /api/dashboard
│     │  ├─ forecast.py                  # GET/POST /api/forecast/*
│     │  ├─ scenario.py                  # POST /api/scenario/whatif
│     │  ├─ campaign.py                  # POST /api/campaign/impact
│     │  ├─ inventory.py                 # GET /api/inventory/recommend
│     │  ├─ data_api.py                  # GET /api/data/exogenous
│     │  ├─ market_intel.py              # GET /api/market/intelligence
│     │  ├─ monitoring.py                # GET /api/monitoring
│     │  ├─ models_registry.py           # GET /api/models/*
│     │  └─ __pycache__/                 # Compiled Python cache (auto-generated)
│     │
│     ├─ services/                       # Business Logic Layer
│     │  ├─ market_intel_services.py     # Market intelligence service functions
│     │  └─ __pycache__/                 # Compiled Python cache (auto-generated)
│     │
│     ├─ templates/                      # HTML Templates
│     │  └─ index.html
│     │
│     ├─ static/                         # Static Assets
│     │  ├─ css/
│     │  │  └─ style.css
│     │  └─ js/
│     │     └─ main.js
│     │
│     └─ __pycache__/                    # Compiled Python cache (auto-generated)
│
└─ frontend/                             # Frontend Files (Optional)
   ├─ static/
   │  ├─ css/
   │  │  └─ style.css
   │  └─ js/
   │     └─ main.js
   └─ templates/
      └─ index.html
```

### Folder Descriptions

| Folder | Purpose |
|--------|---------|
| `backend/` | Flask REST API server |
| `backend/denso_app/` | Main application package |
| `backend/denso_app/api/` | Blueprint routes (modular endpoints) |
| `backend/denso_app/services/` | Business logic & service functions |
| `backend/denso_app/core/` | Constants & shared utilities |
| `backend/denso_app/static/` | CSS, JS, images |
| `backend/denso_app/templates/` | HTML templates |
| `frontend/` | Optional frontend assets |

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
cd backend
python run.py
```

Server will start at `http://localhost:5000`


<br>

---
## 🗄 1. HƯỚNG DẪN SỬ DỤNG POSTGRESQL QUA DOCKER
---

SYSTEM: PostgreSQL 16 + pgAdmin 4 (UI)

------------------------------------
1.1 Khởi động database
------------------------------------
Tại thư mục dự án:
```
docker compose up -d
```
Kiểm tra:
```
docker ps
```
------------------------------------
1.2 Truy cập PostgreSQL
------------------------------------

Cách 1 – từ host:
```

psql -h localhost -p 5432 -U denso -d denso_forecast
# password: admin
```
Cách 2 – từ trong terminal vscode:
```
docker exec -it denso_db_local psql -U denso -d denso_forecast
```
------------------------------------
1.3 Nạp schema + seed data
------------------------------------
```
psql -h localhost -p 5432 -U denso -d denso_forecast -f schema.sql
psql -h localhost -p 5432 -U denso -d denso_forecast -f seed_data.sql
psql -h localhost -p 5432 -U denso -d denso_forecast -f seed_alter_v3.sql
```
------------------------------------
1.4 Truy cập pgAdmin (GUI)
------------------------------------

Tải về pgAdmin4 về

Thêm server mới:
- Name: denso_local
- Host: db
- Port: 5432
- Database: denso_forecast
- User: denso
- Pass: admin

------------------------------------
1.5 Config Flask kết nối Postgres
------------------------------------

Trong file .env:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=denso_forecast
DB_USER=denso
DB_PASSWORD=admin
```
Nếu backend chạy trong container → DB_HOST=db.

<br>

---
## 2. LUỒNG DỮ LIỆU HỆ THỐNG
---

Collector Agent  
    → mart.market_news_storage  
    → mart.market_news_summary  
    → Backend API  
    → Dashboard (Market Intelligence News)

Prophet / XGBoost Pipeline  
    → generate_forecasts.py  
    → mart.demand_forecast_weekly  
    → /api/forecast → UI (SKU Forecast)

Public Data (NOAA/IEA/VAMA/Google Trends)  
    → Collector Agent scheduler  
    → Storage mart.*

<br>

---
## 3. KẾT LUẬN
---

- Cấu trúc project theo chuẩn enterprise.
- Backend + Service Layer rõ ràng.
- AI Workspace gồm Forecast engine + Data Collector Agent.
- PostgreSQL làm nguồn dữ liệu trung tâm.
- Docker-compose giúp setup DB/pgAdmin trong 10 giây.
- Dễ mở rộng sang cloud, CI/CD, Kubernetes.