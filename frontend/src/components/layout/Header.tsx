import React from 'react';
import { SystemHealth, SystemStatus } from '../../services/api';
import { ShieldCheck, Cpu, RefreshCw } from 'lucide-react';

interface HeaderProps {
  health: SystemHealth | null;
  status: SystemStatus | null;
  isLoading: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ health, status, isLoading, onRefresh }) => {
  const isConnected = health?.status === 'healthy';

  return (
    <header className="h-16 bg-navy-900/80 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Track & Title */}
      <div className="flex items-center space-x-3">
        <span className="px-2.5 py-1 text-[11px] font-semibold rounded-md bg-electric-500/10 text-electric-400 border border-electric-500/20">
          Razorpay Track 3 — AI Revenue Recovery
        </span>
        <span className="text-slate-600">|</span>
        <div className="flex items-center space-x-2 text-xs text-slate-400">
          <Cpu className="w-3.5 h-3.5 text-slate-400" />
          <span>Agent Model: <strong className="text-slate-200 font-mono">GPT-4o-mini + Safety Policy Engine</strong></span>
        </div>
      </div>

      {/* Live System Status Badges */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-700 transition-colors disabled:opacity-50"
          title="Refresh Status"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>

        {/* Razorpay Test Mode Badge */}
        <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-800/90 border border-slate-700 text-[11px]">
          <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
          <span className="text-slate-300 font-medium">Razorpay TEST MODE</span>
        </div>

        {/* Policy Guardrail Badge */}
        <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-800/90 border border-emerald-500/30 text-[11px]">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-emerald-300 font-medium">Policy Engine: ACTIVE</span>
        </div>

        {/* Backend Connection Health */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-navy-950 border border-slate-800 text-[11px]">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-slate-300 font-medium">
            Backend: {isConnected ? 'CONNECTED' : 'ACTIVE (DEMO)'}
          </span>
        </div>
      </div>
    </header>
  );
};
