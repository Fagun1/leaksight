# LeakSight — AI-Powered Tech Leak Intelligence Platform

LeakSight collects, classifies, and surfaces technology rumors and leaks from **forums**, **tech news sites**, and **tech blogs** in real time. No API keys required.

## Features

- **Multi-source scraping**: Forums (MacRumors, Overclock.net, LTT), MacRumors, NotebookCheck, TechRadar
- **NLP leak detection**: Classifies posts as leak vs non-leak
- **Entity extraction**: Companies, products, features from text
- **Credibility scoring**: Rumor credibility based on source history and corroboration
- **Trending detection**: Identifies leaks gaining traction
- **Dashboard**: Next.js frontend with charts, tables, and filters

## Prerequisites

- Python 3.11+
- Node.js 20+
- **MongoDB Atlas** (free tier) — [cloud.mongodb.com](https://cloud.mongodb.com)
- **Redis Cloud** (free tier) — [redis.com/try-free](https://redis.com/try-free)

## Quick Start

### 1. Clone and setup

```bash
cd leaksight
cp env.example .env
```

### 2. Configure MongoDB Atlas and Redis Cloud

1. **MongoDB Atlas**  
   - Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com)  
   - Create a database user (username + password)  
   - Get the connection string: **Connect** → **Drivers** → copy the URI  
   - In `.env`, set `MONGO_URI` to your connection string (replace `<password>` with your user password; URL-encode special characters like `@` as `%40`)

2. **Redis Cloud**  
   - Create a free database at [redis.com/try-free](https://redis.com/try-free)  
   - Copy the connection URL from the database details  
   - In `.env`, set `REDIS_URL` to your Redis URL (usually starts with `rediss://`)

### 3. Backend

```bash
cd leaksight
pip install -r backend/requirements.txt
# Windows PowerShell: $env:PYTHONPATH = (Get-Location).Path
# Linux/Mac: export PYTHONPATH=$(pwd)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Seed sample data

```bash
# From project root
python -m infra.scripts.seed_db
```

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000/dashboard

### 6. Get real data

1. (Optional) Add **forum seed URLs** via API for more sources:
   ```bash
   curl -X POST http://localhost:8000/api/v1/seeds -H "Content-Type: application/json" -d '{"url":"https://forums.macrumors.com/forums/iphone.100/","domain":"forums.macrumors.com","category":"forum","priority":9}'
   ```
2. Click **"Scrape"** (or "Fetch real data now") on the dashboard. The backend will fetch from **Forums**, **MacRumors**, **NotebookCheck**, and **TechRadar**, then run leak detection and store results. **No API keys required.**

## Project Structure

```
leaksight/
├── backend/           # FastAPI, scrapers, AI, services
│   ├── api/v1/        # REST endpoints
│   ├── scraper/       # Forum, MacRumors, NotebookCheck, TechRadar scrapers
│   ├── pipeline/      # Text cleaning, dedup
│   ├── ai/            # Classifier, entity extractor
│   ├── services/      # Credibility, trending
│   └── db/            # MongoDB, Redis clients
├── frontend/          # Next.js 14, Tailwind, Tremor
├── infra/scripts/     # Seed, backup scripts
└── data/              # Models, training data
```

## API Endpoints

| Endpoint | Description |
|---------|-------------|
| `GET /api/v1/rumors` | List rumors with filters |
| `GET /api/v1/rumors/{id}` | Rumor detail with posts |
| `GET /api/v1/trending` | Trending leaks |
| `GET /api/v1/posts` | Raw scraped posts |
| `GET /api/v1/entities` | Extracted entities |
| `GET /api/v1/sources` | Source credibility |
| `GET /api/v1/alerts` | Alert subscriptions |
| `POST /api/v1/scrape` | Trigger scrape (Forums + tech sites) |
| `GET /api/v1/seeds` | List seed URLs (crawler config) |
| `POST /api/v1/seeds` | Add seed URL |

## Environment Variables

See `env.example`. Key variables:

- `MONGO_URI` — MongoDB Atlas connection string (e.g. `mongodb+srv://user:pass@cluster.mongodb.net/leaksight`)
- `REDIS_URL` — Redis Cloud connection URL (e.g. `rediss://default:pass@host:port`)
- `NEXT_PUBLIC_API_URL` — Backend URL for frontend (e.g. `http://localhost:8000/api/v1`)
- Scrapers use Forums, MacRumors, NotebookCheck, TechRadar — **no API keys required**

## License

MIT
