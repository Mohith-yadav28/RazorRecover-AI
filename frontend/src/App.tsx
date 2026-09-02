import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { RecoveryProvider } from './context/RecoveryContext';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { RevenueAtRisk } from './pages/RevenueAtRisk';
import { Cases } from './pages/Cases';
import { CaseDetail } from './pages/CaseDetail';
import { AgentChat } from './pages/AgentChat';
import { ActivityTimeline } from './pages/ActivityTimeline';
import { AuditTrail } from './pages/AuditTrail';
import { Analytics } from './pages/Analytics';
import { Policies } from './pages/Policies';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <RecoveryProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="risk" element={<RevenueAtRisk />} />
            <Route path="cases" element={<Cases />} />
            <Route path="cases/:id" element={<CaseDetail />} />
            <Route path="agent" element={<AgentChat />} />
            <Route path="activity" element={<ActivityTimeline />} />
            <Route path="audit" element={<AuditTrail />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="policies" element={<Policies />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </RecoveryProvider>
    </BrowserRouter>
  );
};

export default App;
