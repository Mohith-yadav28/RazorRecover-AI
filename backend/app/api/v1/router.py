from fastapi import APIRouter
from app.api.v1 import health, transactions, cases, analytics, policies, ml, agent, razorpay

api_router = APIRouter()
api_router.include_router(health.router, prefix="/system", tags=["System"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(cases.router, prefix="/cases", tags=["Recovery Cases"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(policies.router, prefix="/policies", tags=["Policy Engine"])
api_router.include_router(ml.router, prefix="/ml", tags=["ML Recovery Model"])
api_router.include_router(agent.router, prefix="/agent", tags=["AI Agent Orchestrator"])
api_router.include_router(razorpay.router, prefix="/razorpay", tags=["Razorpay Test Mode & Simulator"])




