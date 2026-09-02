import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchTransactions, runAgentWorkflow, Transaction } from '../services/api';
import { useRecovery } from '../context/RecoveryContext';
import { TrendingDown, Search, Filter, Play, CheckCircle2, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';

export const RevenueAtRisk: React.FC = () => {
  const navigate = useNavigate();
  const { refreshRecoveryState } = useRecovery();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [runningId, setRunningId] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchTransactions({
        limit: 50,
        status: statusFilter || undefined,
        search: searchQuery || undefined
      });
      setTransactions(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleRunAgent = async (txnId: string) => {
    setRunningId(txnId);
    try {
      const res = await runAgentWorkflow(txnId);
      await refreshRecoveryState();
      if (res && res.case_id) {
        navigate(`/cases/${res.case_id}`);
      }
    } finally {
      setRunningId(null);
    }
  };


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-rose-400" />
            Revenue at Risk Directory
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Detect and inspect silently failing transactions across gateway timeouts, abandoned carts, and subscription failures.
          </p>
        </div>
        <button
          onClick={loadData}
          className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white border border-slate-700 text-xs font-semibold flex items-center space-x-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-xl bg-navy-900 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <form onSubmit={handleSearch} className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Transaction ID, Customer Name or Email..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-navy-950 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-electric-500"
          />
        </form>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-navy-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-electric-500"
          >
            <option value="">All Statuses</option>
            <option value="FAILED">FAILED</option>
            <option value="ABANDONED">ABANDONED</option>
            <option value="RECOVERED">RECOVERED</option>
          </select>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="rounded-xl bg-navy-900 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-950 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="p-3.5">Transaction ID</th>
                <th className="p-3.5">Customer</th>
                <th className="p-3.5">Amount</th>
                <th className="p-3.5">Failure Reason</th>
                <th className="p-3.5">Method</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {transactions.map((txn) => (
                <tr key={txn.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5 font-mono font-semibold text-slate-200">{txn.id}</td>
                  <td className="p-3.5">
                    <div className="font-semibold text-slate-200">{txn.customer?.name || 'Customer'}</div>
                    <div className="text-[10px] text-slate-400">{txn.customer?.email || ''}</div>
                  </td>
                  <td className="p-3.5 font-mono font-bold text-slate-100">
                    ₹{txn.amount.toLocaleString('en-IN')}
                  </td>
                  <td className="p-3.5 font-mono text-rose-400">
                    {txn.failure_reason || 'UNKNOWN'}
                  </td>
                  <td className="p-3.5 font-mono text-slate-400">{txn.payment_method || 'UPI'}</td>
                  <td className="p-3.5">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono ${
                      txn.recovered ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      txn.status === 'ABANDONED' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    }`}>
                      {txn.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => handleRunAgent(txn.id)}
                      disabled={runningId === txn.id}
                      className="px-3 py-1.5 rounded-lg bg-electric-600 hover:bg-electric-500 text-white font-semibold text-[11px] flex items-center space-x-1.5 ml-auto transition-colors disabled:opacity-50"
                    >
                      <Play className="w-3 h-3 fill-white" />
                      <span>{runningId === txn.id ? 'Running...' : 'Run Agent'}</span>
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
