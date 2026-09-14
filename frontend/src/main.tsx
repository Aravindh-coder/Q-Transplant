import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import '../app/globals.css';
import { AuthProvider } from '../lib/auth';
import { NavBar } from '../components/NavBar';
import Home from '../app/page';
import QuantumVisualizer from '../app/quantum/page';
import DoctorDashboard from '../app/dashboard/doctor/page';
import OrganizerDashboard from '../app/dashboard/organizer/page';
import HospitalDashboard from '../app/dashboard/hospital/page';
import DonorDashboard from '../app/dashboard/donor/page';

function App() {
  const [pathname, setPathname] = useState(window.location.pathname || '/');

  useEffect(() => {
    const handleLocationChange = () => setPathname(window.location.pathname);
    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  const renderCurrentView = () => {
    if (pathname === '/quantum') return <QuantumVisualizer />;
    if (pathname.startsWith('/dashboard/doctor')) return <DoctorDashboard />;
    if (pathname.startsWith('/dashboard/organizer')) return <OrganizerDashboard />;
    if (pathname.startsWith('/dashboard/hospital')) return <HospitalDashboard />;
    if (pathname.startsWith('/dashboard/donor')) return <DonorDashboard />;
    return <Home />;
  };

  return (
    <AuthProvider>
      <div className="min-h-screen flex flex-col">
        <NavBar />
        <main className="flex-1 max-w-7xl w-full mx-auto p-6">
          {renderCurrentView()}
        </main>
        <footer className="py-6 border-t border-slate-900 text-center text-xs text-slate-500">
          <p>Q-Transplant Quantum Architecture • Clinical Decision Support • Decision approval by authorized transplant teams</p>
        </footer>
      </div>
    </AuthProvider>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
