import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useRecovery } from '../context/RecoveryContext';
import { DemoScenarioBar } from '../components/demo/DemoScenarioBar';
import { Zap, Play, RotateCcw, BarChart, ShieldCheck, Database, Clock } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const {
    summary,
    failureMetrics,
    loading,
    scanning,
    resetting,
    lastUpdated,
    calculateRevenueAtRisk,
    calculateEligibleRecoverable,
    calculateRecoveredRevenue,
    calculateHumanEscalations,
    runBatchScan,
    resetDemo
  } = useRecovery();

  const handleScenarioLoaded = (caseId: string) => {
    navigate(`/cases/${caseId}`);
  };

  const revAtRisk = calculateRevenueAtRisk();
  const eligibleRev = calculateEligibleRecoverable();
  const recoveredRev = calculateRecoveredRevenue();
  const escalations = calculateHumanEscalations();

  return (
    <div className="space-y-6">
      {/* Executive Hero Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-navy-900 via-navy-850 to-navy-900 border border-slate-800 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-electric-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center space-x-2 text-electric-400 font-semibold text-xs uppercase tracking-wider mb-1">
              <Zap className="w-3.5 h-3.5" />
              <span>RazorRecover AI Autonomous Revenue Recovery Platform</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
              Executive Revenue Recovery Control Center
            </h1>
            <p className="text-slate-400 text-sm mt-1 max-w-2xl leading-relaxed">
              Detect silently failing transactions, diagnose root causes, execute bounded recovery interventions, and measure exact financial yield.
            </p>
            {/* Metadata Indicators */}
            <div className="flex flex-wrap items-center gap-3 mt-3 text-xs text-slate-400 font-mono">
              <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700">
                <Database className="w-3.5 h-3.5 text-electric-400" />
                <span>DATASET: {summary ? summary.total_transactions.toLocaleString() : '5,001'} Records</span>
              </span>
              <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700">
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                <span>LAST EVALUATED: {lastUpdated.toLocaleTimeString()}</span>
              </span>
              <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                <span>MODE: RAZORPAY TEST & DEMO SIMULATOR</span>
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => runBatchScan(300)}
              disabled={scanning || resetting}
              className="px-4 py-2.5 rounded-xl bg-electric-600 hover:bg-electric-500 text-white font-semibold text-xs flex items-center space-x-2 transition-all shadow-lg shadow-electric-600/30 disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{scanning ? 'Scanning Batch...' : 'RUN RECOVERY SCAN'}</span>
            </button>

            <button
              onClick={() => resetDemo()}
              disabled={scanning || resetting}
              className="px-3.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs flex items-center space-x-2 transition-all border border-slate-700 disabled:opacity-50"
            >
              <RotateCcw className={`w-3.5 h-3.5 ${resetting ? 'animate-spin' : ''}`} />
              <span>{resetting ? 'Resetting...' : 'RESET DEMO'}</span>
            </button>

            <div className="px-3.5 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center space-x-2 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              <span>AGENT ACTIVE</span>
            </div>
          </div>
        </div>
      </div>

      {/* Demo Scenario Quick-Run Bar */}
      <DemoScenarioBar onScenarioLoaded={handleScenarioLoaded} />

      {/* KPI Overview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Revenue at Risk */}
        <div className="p-5 rounded-xl bg-navy-900 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Revenue at Risk</span>
            <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-mono text-[10px]">High Priority</span>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-slate-100 font-mono">
              {loading ? '...' : `₹${revAtRisk.toLocaleString('en-IN')}`}
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Across failed payments & abandoned checkouts</p>
        </div>

        {/* Card 2: Recoverable Value */}
        <div className="p-5 rounded-xl bg-navy-900 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Eligible Recoverable</span>
            <span className="px-2 py-0.5 rounded bg-electric-500/10 text-electric-400 border border-electric-500/20 font-mono text-[10px]">ML Prob &ge; 75%</span>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-electric-400 font-mono">
              {loading ? '...' : `₹${eligibleRev.toLocaleString('en-IN')}`}
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Targeted by safe automated agent retries</p>
        </div>

        {/* Card 3: Recovered Revenue */}
        <div className="p-5 rounded-xl bg-navy-900 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Recovered Revenue</span>
            <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono text-[10px]">Proven ROI</span>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-emerald-400 font-mono">
              {loading ? '...' : `₹${recoveredRev.toLocaleString('en-IN')}`}
            </span>
            <span className="text-xs text-emerald-400 font-mono">
              {summary ? summary.recovery_rate : 0}% rate
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Verified payment recovery receipts</p>
        </div>

        {/* Card 4: Human Escalations */}
        <div className="p-5 rounded-xl bg-navy-900 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Human Escalations</span>
            <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono text-[10px]">Bounded Policy</span>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-amber-400 font-mono">
              {loading ? '...' : escalations} Cases
            </span>
          </div>
          <p className="text-[11px] text-slate-400">High-value (&gt;₹50,000) or suspicious cases</p>
        </div>
      </div>

      {/* Failure Reason Distribution Table */}
      <div className="p-5 rounded-xl bg-navy-900 border border-slate-800 space-y-4">
        <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
          <BarChart className="w-4 h-4 text-electric-400" />
          <span>Failure Category & Recovery Yield Breakdown</span>
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-950 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="p-3">Failure Reason</th>
                <th className="p-3">Count</th>
                <th className="p-3">Total Revenue at Risk</th>
                <th className="p-3">Recovered Revenue</th>
                <th className="p-3">Yield Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {failureMetrics.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3 font-semibold font-mono text-slate-200">{item.failure_reason}</td>
                  <td className="p-3">{item.count.toLocaleString()}</td>
                  <td className="p-3 font-mono text-rose-400">₹{item.total_at_risk.toLocaleString('en-IN')}</td>
                  <td className="p-3 font-mono text-emerald-400">₹{item.total_recovered.toLocaleString('en-IN')}</td>
                  <td className="p-3 font-mono font-bold text-electric-400">{item.recovery_rate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
