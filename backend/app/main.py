from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import Base, engine, SessionLocal
from app.core.seed import seed_database_if_empty

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Auto-seed database if empty
with SessionLocal() as db_session:
    seed_database_if_empty(db_session)

app = FastAPI(

    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="RazorRecover AI — Bounded Autonomous Revenue Recovery Engine for Razorpay Track 3."
)

# Set CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "Welcome to RazorRecover AI Backend Engine",
        "tagline": "Detect. Decide. Recover. Measure.",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/system/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
