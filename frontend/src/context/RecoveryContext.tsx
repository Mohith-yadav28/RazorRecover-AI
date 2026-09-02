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
  const [summary, setSummary] = useState<RevenueMetricsSummary | null>(null);
  const [cases, setCases] = useState<RecoveryCase[]>([]);
  const [failureMetrics, setFailureMetrics] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [scanning, setScanning] = useState<boolean>(false);
  const [resetting, setResetting] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const refreshRecoveryState = useCallback(async () => {
    try {
      const [sumData, failData, casesData] = await Promise.all([
        fetchAnalyticsSummary().catch(() => null),
        fetchMetricsByFailureReason().catch(() => []),
        fetchRecoveryCases().catch(() => [])
      ]);
      setSummary(sumData);
      setFailureMetrics(failData);
      setCases(casesData);
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshRecoveryState();
  }, [refreshRecoveryState]);

  const runBatchScan = async (limit: number = 300) => {
    setScanning(true);
    try {
      await triggerBatchScan(limit);
      await refreshRecoveryState();
    } finally {
      setScanning(false);
    }
  };

  const resetDemo = async () => {
    setResetting(true);
    try {
      await resetDemoState();
      await refreshRecoveryState();
    } finally {
      setResetting(false);
    }
  };

  const calculateRevenueAtRisk = useCallback((): number => {
    return summary ? summary.revenue_at_risk : 0;
  }, [summary]);

  const calculateEligibleRecoverable = useCallback((): number => {
    return summary ? summary.eligible_recovery_value : 0;
  }, [summary]);

  const calculateRecoveredRevenue = useCallback((): number => {
    return summary ? summary.revenue_recovered : 0;
  }, [summary]);

  const calculateHumanEscalations = useCallback((): number => {
    return summary ? summary.human_escalations : 0;
  }, [summary]);

  return (
    <RecoveryContext.Provider
      value={{
        summary,
        cases,
        failureMetrics,
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
