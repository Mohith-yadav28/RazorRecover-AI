import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { fetchSystemHealth, fetchSystemStatus, SystemHealth, SystemStatus } from '../../services/api';

export const Layout: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const checkHealth = async () => {
    setIsLoading(true);
    try {
      const [h, s] = await Promise.all([
        fetchSystemHealth().catch(() => null),
        fetchSystemStatus().catch(() => null),
      ]);
      setHealth(h);
      setStatus(s);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex min-h-screen bg-navy-950 text-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header health={health} status={status} isLoading={isLoading} onRefresh={checkHealth} />
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet context={{ health, status }} />
        </main>
      </div>
    </div>
  );
};
