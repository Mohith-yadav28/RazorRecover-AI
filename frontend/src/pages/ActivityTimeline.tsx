import React, { useEffect, useState } from 'react';
import { fetchAuditTrail, AuditEvent } from '../services/api';
import { Activity, CheckCircle2, ShieldCheck, Cpu, RefreshCw } from 'lucide-react';

export const ActivityTimeline: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const loadTrail = async () => {
    setLoading(true);
    try {
      const data = await fetchAuditTrail(30);
      setEvents(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrail();
  }, []);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Activity className="w-5 h-5 text-electric-400" />
            Agent Activity Live Feed
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time visual progress of the 10-step agentic workflow loop (OBSERVE → INVESTIGATE → SCORE → REASON → POLICY → EXECUTE → VERIFY → MEASURE).
          </p>
        </div>

        <button
          onClick={loadTrail}
          className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white border border-slate-700 text-xs font-semibold flex items-center space-x-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Feed</span>
        </button>
      </div>

      {/* Timeline Steps */}
      <div className="p-6 rounded-xl bg-navy-900 border border-slate-800 space-y-6">
        <div className="relative border-l-2 border-slate-800 ml-4 space-y-6 pl-6">
          {events.map((evt) => (
            <div key={evt.id} className="relative group">
              {/* Timeline Dot */}
              <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-navy-950 border-2 border-electric-400 flex items-center justify-center">
                <div className="w-1.5 h-1.5 rounded-full bg-electric-400"></div>
              </div>

              <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 hover:border-electric-500/30 transition-colors space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-electric-500/10 text-electric-400 border border-electric-500/20">
                      {evt.agent_step}
                    </span>
                    <span className="text-xs font-semibold text-slate-200">{evt.event_type}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {new Date(evt.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div className="text-xs font-mono text-slate-100 font-semibold">{evt.decision}</div>
                {evt.reason && <div className="text-xs text-slate-400 leading-relaxed">{evt.reason}</div>}

                {evt.recovered_amount > 0 && (
                  <div className="text-xs font-mono font-bold text-emerald-400">
                    Revenue Recovered: ₹{evt.recovered_amount.toLocaleString('en-IN')}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
