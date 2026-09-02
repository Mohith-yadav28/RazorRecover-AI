import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchRecoveryCaseDetail, runAgentWorkflow, createRazorpayPaymentLink, RecoveryCase } from '../services/api';
import { useRecovery } from '../context/RecoveryContext';
import { ShieldCheck, AlertTriangle, CheckCircle2, XCircle, ArrowLeft, Play, Link, User, CreditCard, Clock, Activity } from 'lucide-react';

export const CaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { refreshRecoveryState } = useRecovery();
  const [caseDetail, setCaseDetail] = useState<RecoveryCase | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [running, setRunning] = useState<boolean>(false);
  const [paymentLink, setPaymentLink] = useState<any | null>(null);

  const loadCase = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await fetchRecoveryCaseDetail(id);
      setCaseDetail(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCase();
  }, [id]);

  const handleExecuteAgent = async () => {
    if (!caseDetail) return;
    setRunning(true);
    try {
      const isHumanRequired = caseDetail.policy_result === 'HUMAN_APPROVAL_REQUIRED' || caseDetail.status === 'ESCALATED';
      await runAgentWorkflow(caseDetail.transaction_id, isHumanRequired);
      await loadCase();
      await refreshRecoveryState();
    } finally {
      setRunning(false);
    }
  };

  const [creatingLink, setCreatingLink] = useState<boolean>(false);
  const [copiedLink, setCopiedLink] = useState<boolean>(false);

  const handleCreatePaymentLink = async () => {
    if (!caseDetail) return;
    setCreatingLink(true);
    setCopiedLink(false);
    try {
      const link = await createRazorpayPaymentLink(caseDetail.transaction_id);
      setPaymentLink(link);
      await loadCase();
      await refreshRecoveryState();
    } catch (e) {
      console.error("Failed to create Razorpay link:", e);
    } finally {
      setCreatingLink(false);
    }
  };


  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 3000);
  };


  if (loading) {
    return <div className="p-8 text-center text-slate-400 text-xs font-mono">Loading case inspection details...</div>;
  }

  if (!caseDetail) {
    return (
      <div className="p-8 text-center space-y-3">
        <div className="text-slate-300 text-sm font-semibold">Recovery Case Not Found</div>
        <button onClick={() => navigate('/cases')} className="px-3 py-1.5 rounded bg-electric-600 text-white text-xs">Back to Cases</button>
      </div>
    );
  }

  const txn = caseDetail.transaction;
  const cust = txn?.customer;
  const exp = caseDetail.ai_explanation;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/cases')}
          className="flex items-center space-x-2 text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Recovery Directory</span>
        </button>

        <div className="flex items-center space-x-3">
          <span className={`px-2.5 py-1 rounded text-xs font-bold font-mono ${
            caseDetail.status === 'RECOVERED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
            caseDetail.status === 'ESCALATED' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
            'bg-slate-800 text-slate-300'
          }`}>
            STATUS: {caseDetail.status}
          </span>
        </div>
      </div>

      {/* Main Hero Card */}
      <div className="p-6 rounded-2xl bg-navy-900 border border-slate-800 space-y-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="text-xs text-slate-400 font-mono">CASE ID: {caseDetail.id}</div>
            <div className="flex items-baseline space-x-3 mt-1">
              <h1 className="text-3xl font-extrabold text-slate-100 font-mono">
                ₹{txn?.amount ? txn.amount.toLocaleString('en-IN') : '0'}
              </h1>
              <span className="text-xs font-mono text-rose-400">
                {txn?.failure_reason ? txn.failure_reason.replace('_', ' ') : 'PAYMENT FAILED'}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-[11px] text-slate-400">ML Recovery Probability</div>
              <div className="text-2xl font-extrabold text-emerald-400 font-mono">
                {Math.round(caseDetail.recovery_probability * 100)}%
              </div>
            </div>
            <div className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase font-mono ${
              caseDetail.priority_tier === 'HIGH' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-electric-500/10 text-electric-400'
            }`}>
              {caseDetail.priority_tier} PRIORITY
            </div>
          </div>
        </div>

        {/* Customer & Failure Diagnostics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Customer History Box */}
          <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 space-y-3">
            <h3 className="text-xs font-bold text-slate-300 flex items-center space-x-2">
              <User className="w-4 h-4 text-electric-400" />
              <span>Customer Profile & History</span>
            </h3>
            <div className="space-y-1.5 text-xs text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Name:</span>
                <span className="font-semibold text-slate-100">{cust?.name || 'Customer'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Email:</span>
                <span className="font-mono text-slate-300">{cust?.email || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Lifetime Value (LTV):</span>
                <span className="font-mono text-emerald-400 font-bold">₹{cust?.lifetime_value ? cust.lifetime_value.toLocaleString('en-IN') : '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Past Successful Payments:</span>
                <span className="font-mono text-slate-200">{cust?.successful_transactions || 0} purchases</span>
              </div>
            </div>
          </div>

          {/* Transaction Diagnostics Box */}
          <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 space-y-3">
            <h3 className="text-xs font-bold text-slate-300 flex items-center space-x-2">
              <CreditCard className="w-4 h-4 text-electric-400" />
              <span>Gateway Diagnostics</span>
            </h3>
            <div className="space-y-1.5 text-xs text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Transaction ID:</span>
                <span className="font-mono text-slate-200">{caseDetail.transaction_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Failure Category:</span>
                <span className="font-mono text-slate-300">{txn?.failure_category || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Payment Method:</span>
                <span className="font-mono text-slate-300">{txn?.payment_method || 'UPI'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Retry Count:</span>
                <span className="font-mono text-slate-200">{txn?.retry_count || 0} / 2 allowed</span>
              </div>
            </div>
          </div>
        </div>

        {/* AI Business Reasoning ("Why?") */}
        <div className="p-5 rounded-xl bg-navy-950 border border-slate-800 space-y-3">
          <h3 className="text-xs font-bold text-electric-400 flex items-center space-x-2 uppercase tracking-wider">
            <Activity className="w-4 h-4" />
            <span>AI Reasoning & Root Cause Diagnosis</span>
          </h3>
          <ul className="space-y-2 text-xs text-slate-300">
            {exp?.why ? (
              exp.why.map((w: string, idx: number) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-electric-400 font-bold">•</span>
                  <span>{w}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-400">Temporary bank timeout diagnosed. High historical payment success rate.</li>
            )}
          </ul>
        </div>

        {/* Policy Evaluation Authorization */}
        <div className="p-5 rounded-xl bg-navy-950 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-emerald-400 flex items-center space-x-2 uppercase tracking-wider">
              <ShieldCheck className="w-4 h-4" />
              <span>Policy Safety Evaluation</span>
            </h3>
            <span className={`px-2.5 py-0.5 rounded text-[11px] font-bold uppercase font-mono ${
              caseDetail.policy_result === 'ALLOWED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
              caseDetail.policy_result === 'HUMAN_APPROVAL_REQUIRED' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
              'bg-rose-500/10 text-rose-400 border border-rose-500/20'
            }`}>
              {caseDetail.policy_result}
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed font-mono">
            {caseDetail.policy_reason || 'All deterministic safety rules evaluated.'}
          </p>

          <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="text-[11px] text-slate-400">Final Authorized Action</div>
              <div className="text-sm font-bold text-slate-100 font-mono">
                {caseDetail.final_action || caseDetail.recommended_action}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {caseDetail.recommended_action === 'CREATE_PAYMENT_LINK' && (
                <button
                  onClick={handleCreatePaymentLink}
                  disabled={creatingLink}
                  className="px-4 py-2 rounded-xl bg-electric-600 hover:bg-electric-500 text-white font-semibold text-xs flex items-center space-x-2 transition-colors disabled:opacity-50"
                >
                  <Link className="w-4 h-4" />
                  <span>{creatingLink ? 'Creating Payment Link...' : 'Generate Razorpay Link'}</span>
                </button>
              )}

              <button
                onClick={handleExecuteAgent}
                disabled={running || caseDetail.status === 'RECOVERED'}
                className={`px-5 py-2.5 rounded-xl text-white font-semibold text-xs flex items-center space-x-2 transition-colors disabled:opacity-50 shadow-lg ${
                  caseDetail.status === 'RECOVERED'
                    ? 'bg-emerald-600/50 cursor-not-allowed'
                    : caseDetail.policy_result === 'HUMAN_APPROVAL_REQUIRED' || caseDetail.status === 'ESCALATED'
                    ? 'bg-amber-600 hover:bg-amber-500 shadow-amber-600/20'
                    : 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/20'
                }`}
              >
                <Play className="w-4 h-4 fill-white" />
                <span>
                  {running
                    ? 'Executing Recovery...'
                    : caseDetail.status === 'RECOVERED'
                    ? 'Payment Fully Recovered'
                    : caseDetail.policy_result === 'HUMAN_APPROVAL_REQUIRED' || caseDetail.status === 'ESCALATED'
                    ? 'Grant Human Approval & Recover'
                    : 'Execute Recovery Intervention'}
                </span>
              </button>
            </div>
          </div>

          {paymentLink && (
            <div className="p-4 rounded-xl bg-slate-900 border border-electric-500/30 text-xs space-y-3 mt-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-emerald-400 font-bold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Payment Link Created ({paymentLink.mode})</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-mono text-[10px] uppercase font-bold">
                  Status: {paymentLink.status || 'created'}
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-navy-950 p-3 rounded-lg border border-slate-800 text-[11px]">
                <div>
                  <span className="text-slate-400 block">Link ID:</span>
                  <span className="font-mono text-slate-200 font-semibold">{paymentLink.payment_link_id}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Amount:</span>
                  <span className="font-mono text-emerald-400 font-bold">₹{paymentLink.amount ? paymentLink.amount.toLocaleString('en-IN') : '0'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Currency:</span>
                  <span className="font-mono text-slate-200">{paymentLink.currency || 'INR'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Short URL:</span>
                  <a
                    href={paymentLink.short_url || paymentLink.payment_link_url}
                    target="_blank"
                    rel="noreferrer"
                    className="font-mono text-electric-400 hover:underline truncate block"
                  >
                    {paymentLink.short_url || paymentLink.payment_link_url}
                  </a>
                </div>
              </div>

              <div className="flex items-center space-x-3 pt-1">
                <a
                  href={paymentLink.short_url || paymentLink.payment_link_url}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3.5 py-1.5 rounded-lg bg-electric-600 hover:bg-electric-500 text-white font-semibold text-xs flex items-center space-x-1.5 transition-colors"
                >
                  <Link className="w-3.5 h-3.5" />
                  <span>Open Payment Link</span>
                </a>

                <button
                  onClick={() => handleCopyLink(paymentLink.short_url || paymentLink.payment_link_url)}
                  className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-colors"
                >
                  {copiedLink ? 'Copied to Clipboard! ✓' : 'Copy Link'}
                </button>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
