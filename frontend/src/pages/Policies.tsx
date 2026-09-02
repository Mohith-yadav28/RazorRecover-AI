import React, { useEffect, useState } from 'react';
import { fetchPolicyRules, PolicyRule } from '../services/api';
import { ShieldAlert, ShieldCheck, CheckCircle2, Lock } from 'lucide-react';

export const Policies: React.FC = () => {
  const [rules, setRules] = useState<PolicyRule[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchPolicyRules().then(setRules).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-emerald-400" />
          Deterministic Policy Guardrail Rules
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Hard Python safety rules that authorize or block every AI agent recovery recommendation.
        </p>
      </div>

      {/* Rules Board */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {rules.map((rule) => (
          <div key={rule.id} className="p-5 rounded-xl bg-navy-900 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="font-mono font-bold text-xs text-slate-100">{rule.rule_code}</span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                ACTIVE
              </span>
            </div>

            <h3 className="text-xs font-bold text-slate-200">{rule.rule_name}</h3>
            <p className="text-xs text-slate-400 leading-relaxed">{rule.description}</p>

            {rule.parameters_json && (
              <div className="p-3 rounded-lg bg-navy-950 border border-slate-800 font-mono text-[11px] text-slate-300">
                <pre>{JSON.stringify(rule.parameters_json, null, 2)}</pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
