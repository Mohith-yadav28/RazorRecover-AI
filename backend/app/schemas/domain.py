from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime

# --- Customer Schemas ---
class CustomerBase(BaseModel):
    name: str
    email: str
    lifetime_value: float = 0.0
    total_transactions: int = 0
    successful_transactions: int = 0
    failed_transactions: int = 0
    is_vip: bool = False
    fraud_score: float = 0.0

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: str
    last_transaction_date: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Transaction Schemas ---
class TransactionBase(BaseModel):
    amount: float
    currency: str = "INR"
    status: str
    failure_reason: Optional[str] = None
    failure_category: Optional[str] = None
    payment_method: Optional[str] = None
    gateway: str = "Razorpay"
    retry_count: int = 0
    is_suspicious: bool = False
    recovered: bool = False
    recovered_amount: float = 0.0

class TransactionCreate(TransactionBase):
    customer_id: str

class TransactionResponse(TransactionBase):
    id: str
    customer_id: str
    created_at: datetime
    recovered_at: Optional[datetime] = None
    customer: Optional[CustomerResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- Recovery Case Schemas ---
class RecoveryCaseBase(BaseModel):
    recovery_probability: float = 0.0
    priority_score: float = 0.0
    priority_tier: str = "MEDIUM"
    recommended_action: Optional[str] = None
    policy_result: str = "PENDING"
    policy_reason: Optional[str] = None
    final_action: Optional[str] = None
    status: str = "OPEN"
    recovered_amount: float = 0.0
    ai_explanation: Optional[Dict[str, Any]] = None

class RecoveryCaseCreate(RecoveryCaseBase):
    transaction_id: str

class RecoveryCaseResponse(RecoveryCaseBase):
    id: str
    transaction_id: str
    created_at: datetime
    updated_at: datetime
    transaction: Optional[TransactionResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- Action Schemas ---
class RecoveryActionBase(BaseModel):
    action_type: str
    provider: str = "RazorpayTestMode"
    razorpay_link_id: Optional[str] = None
    razorpay_link_url: Optional[str] = None
    status: str = "EXECUTED"
    error_message: Optional[str] = None

class RecoveryActionCreate(RecoveryActionBase):
    case_id: str
    transaction_id: str

class RecoveryActionResponse(RecoveryActionBase):
    id: str
    case_id: str
    transaction_id: str
    executed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Audit Event Schemas ---
class AuditEventBase(BaseModel):
    agent_step: str
    event_type: str
    decision: Optional[str] = None
    reason: Optional[str] = None
    policy_name: Optional[str] = None
    result: Optional[str] = None
    recovered_amount: float = 0.0
    details_json: Optional[Dict[str, Any]] = None

class AuditEventCreate(AuditEventBase):
    transaction_id: Optional[str] = None
    case_id: Optional[str] = None

class AuditEventResponse(AuditEventBase):
    id: str
    timestamp: datetime
    transaction_id: Optional[str] = None
    case_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Policy Rule Schemas ---
class PolicyRuleBase(BaseModel):
    rule_code: str
    rule_name: str
    description: str
    is_active: bool = True
    parameters_json: Optional[Dict[str, Any]] = None

class PolicyRuleResponse(PolicyRuleBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Agent Run Schemas ---
class AgentRunBase(BaseModel):
    status: str = "COMPLETED"
    transactions_examined: int = 0
    cases_processed: int = 0
    auto_eligible_count: int = 0
    human_approval_count: int = 0
    stopped_count: int = 0
    successful_recoveries: int = 0
    failed_recoveries: int = 0
    recovered_amount: float = 0.0
    details_json: Optional[Dict[str, Any]] = None

class AgentRunResponse(AgentRunBase):
    id: str
    started_at: datetime
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)



# --- Revenue Summary Schemas ---
class RevenueMetricsSummary(BaseModel):
    total_transactions: int
    total_transaction_value: float
    failed_payment_value: float
    abandoned_checkout_value: float
    subscription_failure_value: float
    revenue_at_risk: float
    eligible_recovery_value: float
    ai_interventions: int
    successful_recoveries: int
    failed_interventions: int
    human_escalations: int
    stopped_cases: int
    revenue_recovered: float
    recovery_rate: float
    intervention_success_rate: float
    average_recovery_time_min: float
