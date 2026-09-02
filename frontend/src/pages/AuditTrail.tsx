import React, { useEffect, useState } from 'react';
import { fetchAuditTrail, AuditEvent } from '../services/api';
import { FileCheck2, Search, RefreshCw, ShieldCheck } from 'lucide-react';

export const AuditTrail: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [stepFilter, setStepFilter] = useState<string>('');

  const loadAuditTrail = async () => {
    setLoading(true);
    try {
      const data = await fetchAuditTrail(50, stepFilter || undefined);
      setEvents(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuditTrail();
  }, [stepFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-emerald-400" />
            Immutable Audit Trail Log
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Complete, auditable record of every observation, diagnosis, ML prediction, policy check, and action execution.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={stepFilter}
            onChange={(e) => setStepFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-navy-900 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-electric-500"
          >
            <option value="">All Agent Steps</option>
            <option value="OBSERVE">OBSERVE</option>
            <option value="SCORE">SCORE</option>
            <option value="POLICY_CHECK">POLICY_CHECK</option>
            <option value="EXECUTE">EXECUTE</option>
            <option value="MEASURE">MEASURE</option>
          </select>
          <button
            onClick={loadAuditTrail}
            className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white border border-slate-700 text-xs font-semibold flex items-center space-x-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Audit Log</span>
          </button>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-xl bg-navy-900 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-950 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="p-3.5">Timestamp</th>
                <th className="p-3.5">Txn ID</th>
                <th className="p-3.5">Step</th>
                <th className="p-3.5">Event Type</th>
                <th className="p-3.5">Decision & Reasoning</th>
                <th className="p-3.5">Policy / Result</th>
                <th className="p-3.5 text-right">Yield</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {events.map((e) => (
                <tr key={e.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5 font-mono text-[10px] text-slate-400">
                    {new Date(e.timestamp).toLocaleString()}
                  </td>
                  <td className="p-3.5 font-mono font-semibold text-slate-200">{e.transaction_id || 'N/A'}</td>
                  <td className="p-3.5">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-electric-500/10 text-electric-400 border border-electric-500/20">
                      {e.agent_step}
                    </span>
                  </td>
                  <td className="p-3.5 font-mono text-slate-300">{e.event_type}</td>
                  <td className="p-3.5 max-w-md">
                    <div className="font-semibold text-slate-100">{e.decision}</div>
                    {e.reason && <div className="text-[11px] text-slate-400 truncate">{e.reason}</div>}
                  </td>
                  <td className="p-3.5 font-mono text-slate-300">{e.result || e.policy_name || 'N/A'}</td>
                  <td className="p-3.5 text-right font-mono font-bold text-emerald-400">
                    {e.recovered_amount > 0 ? `₹${e.recovered_amount.toLocaleString('en-IN')}` : '-'}
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
