from typing import Dict, Any, Tuple
from app.core.config import settings

class PolicyEvaluationResult:
    def __init__(self, policy_result: str, reason: str, final_action: str, rule_code: str):
        self.policy_result = policy_result  # ALLOWED, BLOCKED, HUMAN_APPROVAL_REQUIRED
        self.reason = reason
        self.final_action = final_action     # RETRY_PAYMENT, CREATE_PAYMENT_LINK, SEND_REMINDER, ESCALATE_TO_HUMAN, STOP_RECOVERY
        self.rule_code = rule_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_result": self.policy_result,
            "reason": self.reason,
            "final_action": self.final_action,
            "rule_code": self.rule_code
        }

class PolicyEngine:
    def evaluate(self, recommendation: str, context: Dict[str, Any]) -> PolicyEvaluationResult:
        """
        Evaluates recommended AI action against hard business policies.
        Returns deterministic PolicyEvaluationResult.
        """
        amount = float(context.get("amount", 0.0))
        prob = float(context.get("recovery_probability", 0.0))
        retry_cnt = int(context.get("retry_count", 0))
        is_susp = bool(context.get("is_suspicious", False))
        contact_cnt = int(context.get("contact_count", 0))

        # RULE 5: Fraud / Suspicious Flag -> ESCALATE TO HUMAN
        if is_susp:
            return PolicyEvaluationResult(
                policy_result="BLOCKED",
                reason=f"Suspicious activity detected. Automated action '{recommendation}' blocked.",
                final_action="ESCALATE_TO_HUMAN",
                rule_code="RULE_FRAUD_ESCALATION"
            )

        # RULE 2: High Value Transaction -> HUMAN APPROVAL REQUIRED
        if amount > settings.HUMAN_APPROVAL_THRESHOLD:
            return PolicyEvaluationResult(
                policy_result="HUMAN_APPROVAL_REQUIRED",
                reason=f"Transaction amount (₹{amount:,.2f}) exceeds automatic recovery threshold (₹{settings.HUMAN_APPROVAL_THRESHOLD:,.2f}). Human authorization required.",
                final_action="HUMAN_APPROVAL_REQUIRED",
                rule_code="RULE_HUMAN_APPROVAL"
            )

        # RULE 3: Low Recovery Probability -> STOP RECOVERY
        if prob < settings.MIN_RECOVERY_PROBABILITY:
            return PolicyEvaluationResult(
                policy_result="BLOCKED",
                reason=f"Calculated recovery probability ({prob*100:.0f}%) is below minimum threshold ({settings.MIN_RECOVERY_PROBABILITY*100:.0f}%).",
                final_action="STOP_RECOVERY",
                rule_code="RULE_MIN_PROBABILITY"
            )

        # RULE 4: Retry Cap Reached -> STOP AUTOMATED RETRIES
        if retry_cnt >= settings.MAX_AUTO_RETRIES:
            return PolicyEvaluationResult(
                policy_result="BLOCKED",
                reason=f"Maximum automated payment retry limit reached ({retry_cnt}/{settings.MAX_AUTO_RETRIES}).",
                final_action="STOP_RECOVERY",
                rule_code="RULE_MAX_RETRIES"
            )

        # RULE 6: Customer Contact Cap Reached
        if contact_cnt >= settings.MAX_CUSTOMER_CONTACTS:
            return PolicyEvaluationResult(
                policy_result="BLOCKED",
                reason=f"Maximum customer contact attempts reached ({contact_cnt}/{settings.MAX_CUSTOMER_CONTACTS}).",
                final_action="STOP_RECOVERY",
                rule_code="RULE_MAX_CONTACTS"
            )

        # RULE 1: Automatic Retry Threshold Validation
        if recommendation == "RETRY_PAYMENT":
            if amount > settings.AUTO_RETRY_MAX_AMOUNT:
                return PolicyEvaluationResult(
                    policy_result="BLOCKED",
                    reason=f"Payment retry amount (₹{amount:,.2f}) exceeds maximum auto-retry cap (₹{settings.AUTO_RETRY_MAX_AMOUNT:,.2f}). Switching to payment link.",
                    final_action="CREATE_PAYMENT_LINK",
                    rule_code="RULE_AUTO_RETRY_CAP"
                )
            if prob < settings.AUTO_RETRY_MIN_PROB:
                return PolicyEvaluationResult(
                    policy_result="BLOCKED",
                    reason=f"Recovery probability ({prob*100:.0f}%) insufficient for automated payment retry. Minimum required: {settings.AUTO_RETRY_MIN_PROB*100:.0f}%.",
                    final_action="SEND_RECOVERY_REMINDER",
                    rule_code="RULE_AUTO_RETRY_PROB"
                )

        # ALL POLICIES PASSED -> AUTHORIZED
        return PolicyEvaluationResult(
            policy_result="ALLOWED",
            reason="All deterministic bounded safety rules satisfied.",
            final_action=recommendation,
            rule_code="RULE_AUTHORIZED"
        )

policy_engine = PolicyEngine()
