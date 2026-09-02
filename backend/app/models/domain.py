import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, index=True)
    lifetime_value = Column(Float, default=0.0)
    total_transactions = Column(Integer, default=0)
    successful_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    last_transaction_date = Column(DateTime, default=utc_now)
    is_vip = Column(Boolean, default=False)
    fraud_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)

    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    customer_id = Column(String(50), ForeignKey("customers.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(30), nullable=False, index=True)  # FAILED, ABANDONED, PENDING, RECOVERED
    failure_reason = Column(String(100), nullable=True)     # BANK_TIMEOUT, INSUFFICIENT_FUNDS, CARD_EXPIRED, AUTH_FAILURE, CART_ABANDONED, SUB_EXPIRED
    failure_category = Column(String(50), nullable=True)   # TEMPORARY_GATEWAY, PERMANENT_CUSTOMER, CHECKOUT_ABANDONMENT, SUBSCRIPTION
    payment_method = Column(String(50), nullable=True)     # UPI, CARD, NETBANKING, WALLET
    gateway = Column(String(50), default="Razorpay")
    retry_count = Column(Integer, default=0)
    is_suspicious = Column(Boolean, default=False)
    recovered = Column(Boolean, default=False)
    recovered_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now, index=True)
    recovered_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="transactions")
    recovery_case = relationship("RecoveryCase", back_populates="transaction", uselist=False, cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="transaction", cascade="all, delete-orphan")


class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    transaction_id = Column(String(50), ForeignKey("transactions.id"), nullable=False, unique=True, index=True)
    recovery_probability = Column(Float, default=0.0)
    priority_score = Column(Float, default=0.0)
    priority_tier = Column(String(20), default="MEDIUM")   # HIGH, MEDIUM, LOW
    recommended_action = Column(String(50), nullable=True) # RETRY_PAYMENT, CREATE_PAYMENT_LINK, SEND_RECOVERY_REMINDER, ESCALATE_TO_HUMAN, STOP_RECOVERY
    policy_result = Column(String(30), default="PENDING")   # ALLOWED, BLOCKED, HUMAN_APPROVAL_REQUIRED
    policy_reason = Column(Text, nullable=True)
    final_action = Column(String(50), nullable=True)
    status = Column(String(30), default="OPEN", index=True) # OPEN, IN_PROGRESS, RECOVERED, ESCALATED, STOPPED, FAILED
    recovered_amount = Column(Float, default=0.0)
    ai_explanation = Column(JSON, nullable=True)           # Business facing structured explanation
    created_at = Column(DateTime, default=utc_now, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    transaction = relationship("Transaction", back_populates="recovery_case")
    recovery_actions = relationship("RecoveryAction", back_populates="case", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="case", cascade="all, delete-orphan")


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    case_id = Column(String(50), ForeignKey("recovery_cases.id"), nullable=False, index=True)
    transaction_id = Column(String(50), ForeignKey("transactions.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)      # RETRY_PAYMENT, CREATE_PAYMENT_LINK, SEND_REMINDER, ESCALATE
    provider = Column(String(50), default="RazorpayTestMode")
    razorpay_link_id = Column(String(100), nullable=True)
    razorpay_link_url = Column(String(255), nullable=True)
    status = Column(String(30), default="EXECUTED")       # EXECUTED, SUCCESS, FAILED, PENDING_HUMAN
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=utc_now, index=True)

    case = relationship("RecoveryCase", back_populates="recovery_actions")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=utc_now, index=True)
    transaction_id = Column(String(50), ForeignKey("transactions.id"), nullable=True, index=True)
    case_id = Column(String(50), ForeignKey("recovery_cases.id"), nullable=True, index=True)
    agent_step = Column(String(50), nullable=False)        # OBSERVE, INVESTIGATE, SCORE, REASON, RECOMMEND, POLICY_CHECK, EXECUTE, VERIFY, RECORD, MEASURE
    event_type = Column(String(50), nullable=False)        # AGENT_DECISION, POLICY_EVALUATION, ACTION_EXECUTED, RECOVERY_VERIFIED
    decision = Column(String(100), nullable=True)
    reason = Column(Text, nullable=True)
    policy_name = Column(String(100), nullable=True)
    result = Column(String(50), nullable=True)
    recovered_amount = Column(Float, default=0.0)
    details_json = Column(JSON, nullable=True)

    transaction = relationship("Transaction", back_populates="audit_events")
    case = relationship("RecoveryCase", back_populates="audit_events")


class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    rule_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    parameters_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    status = Column(String(30), default="COMPLETED", index=True) # COMPLETED, IN_PROGRESS, PARTIAL_FAILURE, FAILED
    started_at = Column(DateTime, default=utc_now, index=True)
    completed_at = Column(DateTime, default=utc_now)
    transactions_examined = Column(Integer, default=0)
    cases_processed = Column(Integer, default=0)
    auto_eligible_count = Column(Integer, default=0)
    human_approval_count = Column(Integer, default=0)
    stopped_count = Column(Integer, default=0)
    successful_recoveries = Column(Integer, default=0)
    failed_recoveries = Column(Integer, default=0)
    recovered_amount = Column(Float, default=0.0)
    details_json = Column(JSON, nullable=True)

