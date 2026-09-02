import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchRecoveryCases, RecoveryCase } from '../services/api';
import { Briefcase, ArrowRight, ShieldCheck, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';

export const Cases: React.FC = () => {
  const navigate = useNavigate();
  const [cases, setCases] = useState<RecoveryCase[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [tierFilter, setTierFilter] = useState<string>('');

  const loadCases = async () => {
    setLoading(true);
    try {
      const data = await fetchRecoveryCases({
        limit: 50,
        priority_tier: tierFilter || undefined
      });
      setCases(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, [tierFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-electric-400" />
            AI Recovery Cases Directory
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Prioritized recovery queue evaluated by machine learning probability scoring and deterministic safety guardrails.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={tierFilter}
            onChange={(e) => setTierFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-navy-900 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-electric-500"
          >
            <option value="">All Priority Tiers</option>
            <option value="HIGH">HIGH Priority</option>
            <option value="MEDIUM">MEDIUM Priority</option>
            <option value="LOW">LOW Priority</option>
          </select>
        </div>
      </div>

      {/* Cases Table */}
      <div className="rounded-xl bg-navy-900 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-950 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="p-3.5">Case ID</th>
                <th className="p-3.5">Transaction</th>
                <th className="p-3.5">Probability</th>
                <th className="p-3.5">Priority</th>
                <th className="p-3.5">AI Recommendation</th>
                <th className="p-3.5">Policy Decision</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {cases.map((c) => (
                <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5 font-mono font-semibold text-slate-200">{c.id}</td>
                  <td className="p-3.5 font-mono text-slate-400">{c.transaction_id}</td>
                  <td className="p-3.5">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 h-2 bg-navy-950 rounded-full overflow-hidden border border-slate-800">
                        <div
                          className={`h-full ${
                            c.recovery_probability >= 0.75 ? 'bg-emerald-400' :
                            c.recovery_probability >= 0.50 ? 'bg-electric-400' : 'bg-rose-500'
                          }`}
                          style={{ width: `${c.recovery_probability * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-mono font-bold text-slate-100">{Math.round(c.recovery_probability * 100)}%</span>
                    </div>
                  </td>
                  <td className="p-3.5">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                      c.priority_tier === 'HIGH' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                      c.priority_tier === 'MEDIUM' ? 'bg-electric-500/10 text-electric-400 border border-electric-500/20' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {c.priority_tier}
                    </span>
                  </td>
                  <td className="p-3.5 font-mono text-slate-200">{c.recommended_action || 'N/A'}</td>
                  <td className="p-3.5">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono ${
                      c.policy_result === 'ALLOWED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      c.policy_result === 'HUMAN_APPROVAL_REQUIRED' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    }`}>
                      {c.policy_result}
                    </span>
                  </td>
                  <td className="p-3.5 font-mono font-bold text-slate-100">{c.status}</td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => navigate(`/cases/${c.id}`)}
                      className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                      title="Inspect Case"
                    >
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
