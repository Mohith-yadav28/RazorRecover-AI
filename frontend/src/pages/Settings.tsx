import React from 'react';
import { useRecovery } from '../context/RecoveryContext';
import { Settings as SettingsIcon, Sliders, ShieldCheck, Key, RefreshCw, Zap, Database, Server } from 'lucide-react';

export const Settings: React.FC = () => {
  const { resetting, resetDemo } = useRecovery();

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2 text-electric-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <SettingsIcon className="w-3.5 h-3.5" />
            <span>Platform Configuration</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Merchant System Settings
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Manage Razorpay API integrations, AI agent autonomy limits, and platform configuration.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 1: Merchant Profile & Environment */}
        <div className="p-5 rounded-2xl bg-navy-900 border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Server className="w-4 h-4 text-electric-400" />
            <span>Merchant Profile & Environment</span>
          </h2>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Merchant Name:</span>
              <span className="font-semibold text-slate-100 font-mono">Razorpay Demo Merchant</span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Merchant ID (MID):</span>
              <span className="font-mono text-slate-200 bg-slate-800 px-2 py-0.5 rounded">MID_RAZOR_2026_094</span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Integration Mode:</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono text-[10px]">
                RAZORPAY TEST MODE
              </span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Base Currency:</span>
              <span className="font-mono text-slate-200">INR (₹)</span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Active Dataset Size:</span>
              <span className="font-mono text-slate-200">5,001 Transaction Records</span>
            </div>
          </div>
        </div>

        {/* Section 2: AI Agent & Policy Control */}
        <div className="p-5 rounded-2xl bg-navy-900 border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Sliders className="w-4 h-4 text-electric-400" />
            <span>AI Agent Autonomy Controls</span>
          </h2>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Agentic Orchestrator:</span>
              <span className="font-semibold text-emerald-400 font-mono flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                <span>ACTIVE (10-Step Loop)</span>
              </span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">ML Scoring Model:</span>
              <span className="font-mono text-slate-200">Random Forest (90.51% Acc)</span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Policy Engine Isolation:</span>
              <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono text-[10px]">
                STRICT_BOUNDED_GUARDRAILS
              </span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">High-Value Threshold:</span>
              <span className="font-mono text-amber-400 font-bold">₹50,000.00 (Human Required)</span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Max Retry Cap:</span>
              <span className="font-mono text-slate-200">2 Automated Attempts</span>
            </div>
          </div>
        </div>

        {/* Section 3: Webhook & Razorpay Credentials */}
        <div className="p-5 rounded-2xl bg-navy-900 border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Key className="w-4 h-4 text-electric-400" />
            <span>API Credentials & Webhook Listener</span>
          </h2>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-slate-400 block mb-1">Razorpay Key ID:</span>
              <input
                type="text"
                readOnly
                value="rzp_test_5173_demo_key"
                className="w-full bg-navy-950 border border-slate-800 rounded-lg px-3 py-1.5 font-mono text-slate-300 text-xs"
              />
            </div>

            <div>
              <span className="text-slate-400 block mb-1">Subscribed Webhook Events:</span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">payment.failed</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">order.paid</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">checkout.abandoned</span>
              </div>
            </div>
          </div>
        </div>

        {/* Section 4: System Actions */}
        <div className="p-5 rounded-2xl bg-navy-900 border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2 border-b border-slate-800 pb-3">
            <RefreshCw className="w-4 h-4 text-electric-400" />
            <span>System Maintenance Actions</span>
          </h2>

          <div className="space-y-3 text-xs">
            <p className="text-slate-400 text-xs leading-relaxed">
              Reset the demo database state to restore initial transaction counts, clear interactive payment links, and recalculate baseline KPI metrics.
            </p>

            <button
              onClick={() => resetDemo()}
              disabled={resetting}
              className="w-full py-2.5 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 font-semibold text-xs flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${resetting ? 'animate-spin' : ''}`} />
              <span>{resetting ? 'Resetting Demo State...' : 'RESET DEMO SYSTEM STATE'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
