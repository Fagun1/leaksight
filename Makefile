.PHONY: dev backend frontend seed install-backend install-frontend

dev:
	@echo "Start MongoDB and Redis, then run: make backend (terminal 1) and make frontend (terminal 2)"
	@echo "Backend: http://localhost:8000 | Frontend: http://localhost:3000"

backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

seed:
	PYTHONPATH=. python -m infra.scripts.seed_db

install-backend:
	pip install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install
