import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  fetchAnalyticsSummary,
  fetchMetricsByFailureReason,
  fetchRecoveryCases,
  triggerBatchScan,
  resetDemoState,
  RevenueMetricsSummary,
  RecoveryCase
} from '../services/api';

const DEFAULT_BASELINE_SUMMARY: RevenueMetricsSummary = {
  total_transactions: 5001,
  total_transaction_value: 54933803.92,
  failed_payment_value: 39102198.77,
  abandoned_checkout_value: 2802000.00,
  subscription_failure_value: 12584000.00,
  revenue_at_risk: 41904198.77,
  eligible_recovery_value: 3733491.00,
  ai_interventions: 1250,
  successful_recoveries: 890,
  failed_interventions: 172,
  human_escalations: 440,
  stopped_cases: 148,
  revenue_recovered: 13029605.15,
  recovery_rate: 23.7,
  intervention_success_rate: 71.2,
  average_recovery_time_min: 14.5
};

const DEFAULT_FAILURE_METRICS = [
  { failure_reason: "BANK_TIMEOUT", count: 1842, total_at_risk: 15420000.00, total_recovered: 5820000.00, recovery_rate: 37.7 },
  { failure_reason: "INSUFFICIENT_FUNDS", count: 1210, total_at_risk: 9850000.00, total_recovered: 2140000.00, recovery_rate: 21.7 },
  { failure_reason: "CART_ABANDONED", count: 950, total_at_risk: 8410000.00, total_recovered: 3120000.00, recovery_rate: 37.1 },
  { failure_reason: "GATEWAY_DOWN", count: 680, total_at_risk: 5420000.00, total_recovered: 1650000.00, recovery_rate: 30.4 },
  { failure_reason: "AUTH_FAILURE", count: 319, total_at_risk: 2804198.77, total_recovered: 299605.15, recovery_rate: 10.7 }
];

interface RecoveryContextType {
  summary: RevenueMetricsSummary | null;
  cases: RecoveryCase[];
  failureMetrics: any[];
  loading: boolean;
  scanning: boolean;
  resetting: boolean;
  lastUpdated: Date;
  calculateRevenueAtRisk: () => number;
  calculateEligibleRecoverable: () => number;
  calculateRecoveredRevenue: () => number;
  calculateHumanEscalations: () => number;
  refreshRecoveryState: () => Promise<void>;
  runBatchScan: (limit?: number) => Promise<void>;
  resetDemo: () => Promise<void>;
}

const RecoveryContext = createContext<RecoveryContextType | undefined>(undefined);

export const RecoveryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [summary, setSummary] = useState<RevenueMetricsSummary | null>(DEFAULT_BASELINE_SUMMARY);
  const [cases, setCases] = useState<RecoveryCase[]>([]);
  const [failureMetrics, setFailureMetrics] = useState<any[]>(DEFAULT_FAILURE_METRICS);
  const [loading, setLoading] = useState<boolean>(true);
  const [scanning, setScanning] = useState<boolean>(false);
  const [resetting, setResetting] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const refreshRecoveryState = useCallback(async () => {
    try {
      const [sumData, failData, casesData] = await Promise.all([
        fetchAnalyticsSummary().catch(() => null),
        fetchMetricsByFailureReason().catch(() => null),
        fetchRecoveryCases().catch(() => null)
      ]);
      
      if (sumData && sumData.total_transactions > 0) setSummary(sumData);
      if (failData && failData.length > 0) setFailureMetrics(failData);
      if (casesData && casesData.length > 0) setCases(casesData);

      
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshRecoveryState();
    // Poll backend every 10 seconds to auto-connect when backend wakes up from sleep
    const interval = setInterval(() => {
      refreshRecoveryState();
    }, 10000);
    return () => clearInterval(interval);
  }, [refreshRecoveryState]);

  const runBatchScan = async (limit: number = 300) => {
    setScanning(true);
    try {
      await triggerBatchScan(limit);
      await refreshRecoveryState();
    } catch (e) {
      console.warn("Batch scan running in demo mode", e);
    } finally {
      setScanning(false);
    }
  };

  const resetDemo = async () => {
    setResetting(true);
    try {
      await resetDemoState();
      await refreshRecoveryState();
    } catch (e) {
      setSummary(DEFAULT_BASELINE_SUMMARY);
      setFailureMetrics(DEFAULT_FAILURE_METRICS);
    } finally {
      setResetting(false);
    }
  };

  const calculateRevenueAtRisk = useCallback((): number => {
    return summary ? summary.revenue_at_risk : DEFAULT_BASELINE_SUMMARY.revenue_at_risk;
  }, [summary]);

  const calculateEligibleRecoverable = useCallback((): number => {
    return summary ? summary.eligible_recovery_value : DEFAULT_BASELINE_SUMMARY.eligible_recovery_value;
  }, [summary]);

  const calculateRecoveredRevenue = useCallback((): number => {
    return summary ? summary.revenue_recovered : DEFAULT_BASELINE_SUMMARY.revenue_recovered;
  }, [summary]);

  const calculateHumanEscalations = useCallback((): number => {
    return summary ? summary.human_escalations : DEFAULT_BASELINE_SUMMARY.human_escalations;
  }, [summary]);

  return (
    <RecoveryContext.Provider
      value={{
        summary: summary || DEFAULT_BASELINE_SUMMARY,
        cases,
        failureMetrics: failureMetrics.length > 0 ? failureMetrics : DEFAULT_FAILURE_METRICS,
        loading,
        scanning,
        resetting,
        lastUpdated,
        calculateRevenueAtRisk,
        calculateEligibleRecoverable,
        calculateRecoveredRevenue,
        calculateHumanEscalations,
        refreshRecoveryState,
        runBatchScan,
        resetDemo
      }}
    >
      {children}
    </RecoveryContext.Provider>
  );
};

export const useRecovery = (): RecoveryContextType => {
  const context = useContext(RecoveryContext);
  if (!context) {
    throw new Error('useRecovery must be used within a RecoveryProvider');
  }
  return context;
};
