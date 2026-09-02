from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.domain import Transaction, Customer, RecoveryCase, utc_now
from app.services.razorpay.service import razorpay_service
from app.services.razorpay.scenarios import DEMO_SCENARIOS, load_demo_scenario

router = APIRouter()

class PaymentLinkRequest(BaseModel):
    transaction_id: str

@router.post("/create-link/{transaction_id}")
def create_payment_link_endpoint(transaction_id: str, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
        
    cust = db.query(Customer).filter(Customer.id == txn.customer_id).first()
    cust_name = cust.name if cust else "Valued Merchant Customer"
    cust_email = cust.email if cust else "customer@example.com"

    res = razorpay_service.create_payment_link(
        amount=txn.amount,
        customer_name=cust_name,
        customer_email=cust_email,
        description=f"RazorRecover AI Payment Link for {txn.id}",
        reference_id=txn.id
    )
    
    # Update case action status
    db_case = db.query(RecoveryCase).filter(RecoveryCase.transaction_id == transaction_id).first()
    if db_case:
        db_case.recommended_action = "CREATE_PAYMENT_LINK"
        db_case.final_action = "CREATE_PAYMENT_LINK"
        db_case.status = "IN_PROGRESS"
        db.commit()

    return res

@router.get("/demo-payment-page/{link_id}", response_class=HTMLResponse)
def demo_payment_page(
    link_id: str,
    amount: float = Query(0.0),
    reference_id: str = Query(""),
    db: Session = Depends(get_db)
):
    """
    Renders an interactive Razorpay Test Mode checkout page for demo sandbox links.
    Completing payment marks transaction as RECOVERED in DB and redirects to dashboard.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Razorpay Test Mode Checkout</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #e2e8f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }}
            .card {{ background: #151d30; border: 1px solid #1e293b; border-radius: 16px; width: 100%; max-width: 440px; padding: 32px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); text-align: center; }}
            .badge {{ background: #0284c7; color: white; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block; margin-bottom: 16px; }}
            .logo {{ font-size: 20px; font-weight: 800; color: #38bdf8; margin-bottom: 24px; display: flex; align-items: center; justify-content: center; gap: 8px; }}
            .amount {{ font-size: 36px; font-weight: 800; color: #f8fafc; margin: 12px 0; font-family: monospace; }}
            .details {{ background: #0f172a; border-radius: 12px; padding: 16px; margin: 20px 0; text-align: left; font-size: 13px; color: #94a3b8; }}
            .details div {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
            .details div:last-child {{ margin-bottom: 0; }}
            .details span.val {{ color: #cbd5e1; font-family: monospace; }}
            .btn {{ background: #0284c7; hover: #0369a1; color: white; border: none; border-radius: 12px; width: 100%; padding: 14px; font-size: 15px; font-weight: 700; cursor: pointer; transition: all 0.2s; margin-top: 10px; }}
            .btn:hover {{ background: #0369a1; transform: translateY(-1px); }}
            .footer {{ font-size: 11px; color: #64748b; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <span class="badge">RAZORPAY TEST MODE</span>
            <div class="logo">⚡ RazorRecover AI Checkout</div>
            <div style="color: #94a3b8; font-size: 13px;">Payment Link Sandbox</div>
            <div class="amount">₹{amount:,.2f}</div>
            
            <div class="details">
                <div><span>Link ID:</span><span class="val">{link_id}</span></div>
                <div><span>Reference:</span><span class="val">{reference_id}</span></div>
                <div><span>Currency:</span><span class="val">INR</span></div>
                <div><span>Status:</span><span class="val" style="color:#34d399">ACTIVE</span></div>
            </div>

            <form action="/api/v1/razorpay/complete-demo-payment?reference_id={reference_id}" method="POST">
                <input type="hidden" name="reference_id" value="{reference_id}">
                <button type="submit" class="btn">Pay Now (Simulate Successful Recovery)</button>
            </form>

            
            <div class="footer">Razorpay Test Mode Sandbox Environment — No real money is charged.</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/complete-demo-payment")
def complete_demo_payment(reference_id: str = Query(""), db: Session = Depends(get_db)):
    """
    Simulates payment success when customer pays on the demo page.
    """
    if reference_id:
        txn = db.query(Transaction).filter(Transaction.id == reference_id).first()
        if txn:
            txn.recovered = True
            txn.recovered_amount = txn.amount
            txn.status = "RECOVERED"
            txn.recovered_at = utc_now()
            
            case = db.query(RecoveryCase).filter(RecoveryCase.transaction_id == reference_id).first()
            if case:
                case.status = "RECOVERED"
                case.recovered_amount = txn.amount
            db.commit()

    return HTMLResponse(content="""
        <html>
        <body style="background:#0b0f19; color:white; font-family:sans-serif; text-align:center; padding-top:100px;">
            <h1 style="color:#34d399;">Payment Successful!</h1>
            <p>RazorRecover AI verified payment recovery receipt.</p>
            <p>Redirecting back to dashboard...</p>
            <script>
                setTimeout(function() {
                    window.location.href = "http://localhost:5173/cases";
                }, 2000);
            </script>
        </body>
        </html>
    """)

@router.get("/scenarios")
def get_demo_scenarios():
    return DEMO_SCENARIOS

@router.post("/load-scenario/{scenario_id}")
def load_scenario_endpoint(scenario_id: str, db: Session = Depends(get_db)):
    res = load_demo_scenario(scenario_id, db)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
