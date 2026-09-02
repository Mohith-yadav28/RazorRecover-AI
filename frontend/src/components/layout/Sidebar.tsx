import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingDown,
  Briefcase,
  Bot,
  Activity,
  BarChart3,
  FileCheck2,
  ShieldAlert,
  Settings,
  ShieldCheck,
  Zap
} from 'lucide-react';

const navigationItems = [
  { name: 'Overview', path: '/', icon: LayoutDashboard },
  { name: 'Revenue at Risk', path: '/risk', icon: TrendingDown, badge: '5,000' },
  { name: 'Recovery Cases', path: '/cases', icon: Briefcase },
  { name: 'AI Agent', path: '/agent', icon: Bot, isNew: true },
  { name: 'Live Activity', path: '/activity', icon: Activity },
  { name: 'Audit Trail', path: '/audit', icon: FileCheck2 },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'Policy Rules', path: '/policies', icon: ShieldAlert },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-navy-900 border-r border-slate-800 flex flex-col h-screen sticky top-0 z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-electric-600 to-electric-400 flex items-center justify-center shadow-lg shadow-electric-500/20">
            <Zap className="w-5 h-5 text-white fill-white" />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 tracking-tight text-base flex items-center gap-1.5">
              RazorRecover <span className="text-electric-400 font-extrabold text-xs px-1.5 py-0.5 rounded bg-electric-500/10 border border-electric-500/20">AI</span>
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">Detect. Decide. Recover.</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
          Platform Menu
        </div>
        {navigationItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-electric-600/15 text-electric-400 border border-electric-500/30 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <div className="flex items-center space-x-2.5">
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="px-1.5 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-400 border border-slate-700">
                  {item.badge}
                </span>
              )}
              {item.isNew && (
                <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 uppercase tracking-wider">
                  Agent
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Guardrail Safety Footer */}
      <div className="p-4 m-3 rounded-xl bg-navy-950/80 border border-slate-800/80 text-xs">
        <div className="flex items-center space-x-2 text-emerald-400 font-semibold mb-1">
          <ShieldCheck className="w-4 h-4" />
          <span>Bounded Autonomy</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Deterministic safety engine enforcing hard threshold limits.
        </p>
      </div>
    </aside>
  );
};
