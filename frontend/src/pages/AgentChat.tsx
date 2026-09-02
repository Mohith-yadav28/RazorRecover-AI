import React, { useState } from 'react';
import { queryAgent } from '../services/api';
import { Bot, Send, User, Sparkles, ShieldCheck } from 'lucide-react';

interface ChatMessage {
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
  data?: any;
}

const quickPrompts = [
  "How much revenue is at risk?",
  "How much revenue did we recover today?",
  "Show me cases requiring human approval.",
  "What should I recover first?"
];

export const AgentChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'agent',
      text: "Hello! I am RazorRecover AI, your autonomous revenue recovery assistant. Ask me anything about payment failures, revenue at risk, recovery probability, or human escalation policy rules.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSend = async (textToSend?: string) => {
    const queryText = textToSend || input;
    if (!queryText.trim()) return;

    const userMsg: ChatMessage = {
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const res = await queryAgent(queryText);
      const agentMsg: ChatMessage = {
        sender: 'agent',
        text: res.answer,
        data: res.data,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'agent',
          text: "I experienced a connection issue while querying backend metrics. Please try again.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto flex flex-col h-[calc(100vh-7rem)]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Bot className="w-5 h-5 text-electric-400" />
            AI Conversational Assistant
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Grounded AI interface answering merchant queries strictly using authoritative backend data.
          </p>
        </div>
        <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold flex items-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Grounded Fact Engine</span>
        </div>
      </div>

      {/* Quick Prompts */}
      <div className="flex flex-wrap gap-2">
        {quickPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p)}
            className="px-3 py-1.5 rounded-lg bg-navy-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 hover:text-white transition-colors flex items-center space-x-1.5"
          >
            <Sparkles className="w-3 h-3 text-electric-400" />
            <span>{p}</span>
          </button>
        ))}
      </div>

      {/* Chat Messages Log */}
      <div className="flex-1 bg-navy-900 border border-slate-800 rounded-xl p-4 overflow-y-auto space-y-4">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex items-start space-x-3 ${m.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
              m.sender === 'user' ? 'bg-electric-600 text-white' : 'bg-navy-950 text-electric-400 border border-slate-800'
            }`}>
              {m.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`max-w-xl p-3.5 rounded-xl text-xs space-y-2 ${
              m.sender === 'user'
                ? 'bg-electric-600/20 text-slate-100 border border-electric-500/30'
                : 'bg-navy-950 text-slate-200 border border-slate-800'
            }`}>
              <div className="leading-relaxed whitespace-pre-wrap">{m.text}</div>
              <div className="text-[10px] text-slate-400 text-right">{m.timestamp}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-xs text-slate-400 font-mono animate-pulse">RazorRecover AI is analyzing backend metrics...</div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex items-center space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask RazorRecover AI about revenue at risk, recovery probability, or human approvals..."
          className="flex-1 px-4 py-3 rounded-xl bg-navy-900 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-electric-500"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-5 py-3 rounded-xl bg-electric-600 hover:bg-electric-500 text-white font-semibold text-xs flex items-center space-x-2 transition-colors disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
};
