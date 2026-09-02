# RazorRecover AI — Public Deployment Guide

## Production Deployment Architecture

```
Frontend: Vercel (React 18 + Vite SPA)
Backend:  Render / Railway (FastAPI Async Gateway)
Database: PostgreSQL / SQLite Persistent Storage
```

---

## 1. Frontend Deployment (Vercel)

1. Connect GitHub repository `razorrecover-ai` to [Vercel](https://vercel.com).
2. Set Root Directory to `frontend`.
3. Framework Preset: **Vite**.
4. Build Command: `npm run build`
5. Output Directory: `dist`
6. Add Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-razorrecover-backend.onrender.com/api/v1`

---

## 2. Backend Deployment (Render / Railway)

1. Connect GitHub repository to [Render](https://render.com).
2. Select **Web Service** with Root Directory: `backend`.
3. Build Command: `pip install -r requirements.txt && python ../scripts/generate_synthetic_data.py`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `ENV`: `production`
   - `RAZORPAY_KEY_ID`: `rzp_test_your_key`
   - `RAZORPAY_KEY_SECRET`: `your_secret`

---

## 3. Database Switching (SQLite to PostgreSQL)

To switch from SQLite to production PostgreSQL:
Simply update the `DATABASE_URL` environment variable:
`DATABASE_URL=postgresql://user:password@host:5432/razorrecover_db`

SQLAlchemy ORM will automatically connect and create tables on startup.
