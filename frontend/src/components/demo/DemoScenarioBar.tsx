import React, { useState } from 'react';
import { loadDemoScenario } from '../../services/api';
import { useRecovery } from '../../context/RecoveryContext';
import { Play, CheckCircle2, AlertTriangle, ShieldAlert, XCircle, ArrowRight } from 'lucide-react';

interface DemoScenarioBarProps {
  onScenarioLoaded: (caseId: string) => void;
}

const scenarios = [
  { id: "scenario_1", label: "Scenario 1: Auto Retry", desc: "Bank Timeout ₹4,999 (91% Prob)", icon: Play, badge: "RECOVERED", color: "emerald" },
  { id: "scenario_2", label: "Scenario 2: Payment Link", desc: "Abandoned Cart ₹8,999 (84% Prob)", icon: CheckCircle2, badge: "LINK CREATED", color: "electric" },
  { id: "scenario_3", label: "Scenario 3: Human Approval", desc: "High Value ₹85,000 (68% Prob)", icon: AlertTriangle, badge: "HUMAN REQUIRED", color: "amber" },
  { id: "scenario_4", label: "Scenario 4: Stop Rule", desc: "Max Retries (2/2) ₹3,499", icon: XCircle, badge: "STOPPED", color: "rose" },
  { id: "scenario_5", label: "Scenario 5: Fraud Escalate", desc: "Suspicious Flag ₹20,000", icon: ShieldAlert, badge: "ESCALATED", color: "purple" }
];

export const DemoScenarioBar: React.FC<DemoScenarioBarProps> = ({ onScenarioLoaded }) => {
  const { refreshRecoveryState } = useRecovery();
  const [activeId, setActiveId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleSelectScenario = async (scId: string) => {
    setLoading(true);
    setActiveId(scId);
    try {
      const res = await loadDemoScenario(scId);
      await refreshRecoveryState();
      if (res && res.case_id) {
        onScenarioLoaded(res.case_id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="p-4 rounded-xl bg-navy-900 border border-electric-500/30 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-electric-400 animate-ping"></span>
          <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
            Deterministic Demo Scenario Simulator
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          Click any scenario to instantly test the agentic loop
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2.5">
        {scenarios.map((sc) => {
          const Icon = sc.icon;
          const isActive = activeId === sc.id;
          return (
            <button
              key={sc.id}
              onClick={() => handleSelectScenario(sc.id)}
              disabled={loading}
              className={`p-3 rounded-lg text-left transition-all duration-150 border flex flex-col justify-between space-y-2 ${
                isActive
                  ? 'bg-electric-600/20 border-electric-400 text-slate-100 shadow-md shadow-electric-500/10'
                  : 'bg-navy-950/80 border-slate-800 text-slate-300 hover:bg-slate-800/80 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <Icon className={`w-4 h-4 text-${sc.color}-400`} />
                <span className={`px-1.5 py-0.5 text-[9px] font-bold rounded bg-${sc.color}-500/10 text-${sc.color}-400 border border-${sc.color}-500/20 uppercase`}>
                  {sc.badge}
                </span>
              </div>
              <div>
                <div className="text-xs font-semibold tracking-tight">{sc.label}</div>
                <div className="text-[10px] text-slate-400 truncate">{sc.desc}</div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
