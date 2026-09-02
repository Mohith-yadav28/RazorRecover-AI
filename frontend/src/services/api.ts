const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export interface SystemHealth {
  status: string;
  service: string;
  version: string;
  environment: string;
  database: string;
  timestamp: string;
}

export interface SystemStatus {
  agent_status: string;
  mode: string;
  razorpay_integration: string;
  bounded_policy_engine: string;
  audit_logging: string;
}

export interface RevenueMetricsSummary {
  total_transactions: number;
  total_transaction_value: number;
  failed_payment_value: number;
  abandoned_checkout_value: number;
  subscription_failure_value: number;
  revenue_at_risk: number;
  eligible_recovery_value: number;
  ai_interventions: number;
  successful_recoveries: number;
  failed_interventions: number;
  human_escalations: number;
  stopped_cases: number;
  revenue_recovered: number;
  recovery_rate: number;
  intervention_success_rate: number;
  average_recovery_time_min: number;
}

export interface Customer {
  id: string;
  name: string;
  email: string;
  lifetime_value: number;
  total_transactions: number;
  successful_transactions: number;
  failed_transactions: number;
  is_vip: boolean;
  fraud_score: number;
}


export interface Transaction {
  id: string;
  customer_id: string;
  amount: number;
  currency: string;
  status: string;
  failure_reason: string;
  failure_category: string;
  payment_method: string;
  gateway: string;
  retry_count: number;
  is_suspicious: boolean;
  recovered: boolean;
  recovered_amount: number;
  created_at: string;
  customer?: Customer;
}

export interface RecoveryCase {
  id: string;
  transaction_id: string;
  recovery_probability: number;
  priority_score: number;
  priority_tier: string;
  recommended_action: string;
  policy_result: string;
  policy_reason: string;
  final_action: string;
  status: string;
  recovered_amount: number;
  ai_explanation?: any;
  created_at: string;
  transaction?: Transaction;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  transaction_id?: string;
  case_id?: string;
  agent_step: string;
  event_type: string;
  decision: string;
  reason: string;
  policy_name: string;
  result: string;
  recovered_amount: number;
  details_json?: any;
}

export interface PolicyRule {
  id: string;
  rule_code: string;
  rule_name: string;
  description: string;
  is_active: boolean;
  parameters_json?: any;
}

export interface DemoScenario {
  id: string;
  title: string;
  description: string;
  amount: number;
  customer: any;
  failure_reason: string;
  probability: number;
  priority_tier: string;
  recommended_action: string;
  policy_result: string;
  status: string;
}

export const fetchSystemHealth = async (): Promise<SystemHealth> => {
  const res = await fetch(`${API_BASE_URL}/system/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
};

export const fetchSystemStatus = async (): Promise<SystemStatus> => {
  const res = await fetch(`${API_BASE_URL}/system/status`);
  if (!res.ok) throw new Error('Status check failed');
  return res.json();
};

export const fetchAnalyticsSummary = async (): Promise<RevenueMetricsSummary> => {
  const res = await fetch(`${API_BASE_URL}/analytics/summary`);
  if (!res.ok) throw new Error('Failed to fetch analytics summary');
  return res.json();
};

export const fetchMetricsByFailureReason = async (): Promise<any[]> => {
  const res = await fetch(`${API_BASE_URL}/analytics/by-failure-reason`);
  if (!res.ok) throw new Error('Failed to fetch failure reason metrics');
  return res.json();
};

export const fetchTransactions = async (params: { skip?: number; limit?: number; status?: string; failure_reason?: string; search?: string } = {}): Promise<Transaction[]> => {
  const query = new URLSearchParams();
  if (params.skip !== undefined) query.set('skip', params.skip.toString());
  if (params.limit !== undefined) query.set('limit', params.limit.toString());
  if (params.status) query.set('status', params.status);
  if (params.failure_reason) query.set('failure_reason', params.failure_reason);
  if (params.search) query.set('search', params.search);

  const res = await fetch(`${API_BASE_URL}/transactions?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch transactions');
  return res.json();
};

export const fetchTransactionDetail = async (id: string): Promise<Transaction> => {
  const res = await fetch(`${API_BASE_URL}/transactions/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch transaction ${id}`);
  return res.json();
};

export const fetchRecoveryCases = async (params: { skip?: number; limit?: number; priority_tier?: string; status?: string; policy_result?: string; search?: string } = {}): Promise<RecoveryCase[]> => {
  const query = new URLSearchParams();
  if (params.skip !== undefined) query.set('skip', params.skip.toString());
  if (params.limit !== undefined) query.set('limit', params.limit.toString());
  if (params.priority_tier) query.set('priority_tier', params.priority_tier);
  if (params.status) query.set('status', params.status);
  if (params.policy_result) query.set('policy_result', params.policy_result);
  if (params.search) query.set('search', params.search);

  const res = await fetch(`${API_BASE_URL}/cases?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch recovery cases');
  return res.json();
};

export const fetchRecoveryCaseDetail = async (id: string): Promise<RecoveryCase> => {
  const res = await fetch(`${API_BASE_URL}/cases/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch case ${id}`);
  return res.json();
};

export const runAgentWorkflow = async (txnId: string, humanApproved: boolean = false): Promise<any> => {
  const query = humanApproved ? '?human_approved=true' : '';
  const res = await fetch(`${API_BASE_URL}/agent/run/${txnId}${query}`, { method: 'POST' });
  if (!res.ok) throw new Error('Agent execution failed');
  return res.json();
};

export const triggerBatchScan = async (limit: number = 200): Promise<any> => {
  const res = await fetch(`${API_BASE_URL}/agent/batch-run?limit=${limit}`, { method: 'POST' });
  if (!res.ok) throw new Error('Batch scan execution failed');
  return res.json();
};

export const resetDemoState = async (): Promise<any> => {
  const res = await fetch(`${API_BASE_URL}/health/reset-demo`, { method: 'POST' });
  if (!res.ok) throw new Error('Reset demo failed');
  return res.json();
};




export const queryAgent = async (queryText: string): Promise<{ answer: string; data?: any }> => {
  const res = await fetch(`${API_BASE_URL}/agent/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: queryText })
  });
  if (!res.ok) throw new Error('Agent query failed');
  return res.json();
};

export const fetchAuditTrail = async (limit: number = 50, step?: string): Promise<AuditEvent[]> => {
  const query = new URLSearchParams({ limit: limit.toString() });
  if (step) query.set('agent_step', step);
  const res = await fetch(`${API_BASE_URL}/agent/audit-trail?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch audit trail');
  return res.json();
};

export const fetchPolicyRules = async (): Promise<PolicyRule[]> => {
  const res = await fetch(`${API_BASE_URL}/policies`);
  if (!res.ok) throw new Error('Failed to fetch policy rules');
  return res.json();
};

export const createRazorpayPaymentLink = async (txnId: string): Promise<any> => {
  const res = await fetch(`${API_BASE_URL}/razorpay/create-link/${txnId}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create Razorpay payment link');
  return res.json();
};

export const fetchDemoScenarios = async (): Promise<DemoScenario[]> => {
  const res = await fetch(`${API_BASE_URL}/razorpay/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch demo scenarios');
  return res.json();
};

export const loadDemoScenario = async (scenarioId: string): Promise<any> => {
  const res = await fetch(`${API_BASE_URL}/razorpay/load-scenario/${scenarioId}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to load demo scenario');
  return res.json();
};
