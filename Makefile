# RazorRecover AI Makefile for Evaluators & Developers

.PHONY: help install test train run-backend run-frontend run-evaluation

help:
	@echo "RazorRecover AI Commands:"
	@echo "  make install        Install backend & frontend dependencies"
	@echo "  make test           Run backend pytest test suite (24 tests)"
	@echo "  make train          Train & compare ML models on 80/20 split"
	@echo "  make run-backend    Start FastAPI backend server on port 8000"
	@echo "  make run-frontend   Start React Vite frontend on port 5173"
	@echo "  make run-evaluation Run benchmark evaluation script"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

test:
	PYTHONPATH=backend pytest backend/tests

train:
	PYTHONPATH=backend python backend/app/services/ml/train.py

run-backend:
	PYTHONPATH=backend uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

run-evaluation:
	PYTHONPATH=backend python scripts/run_evaluation.py
