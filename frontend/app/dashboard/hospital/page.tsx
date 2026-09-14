'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../lib/auth';
import { GlassCard } from '../../../components/GlassCard';
import { LifecycleBadge } from '../../../components/LifecycleBadge';
import { apiFetch } from '../../../lib/api';
import { Building2, AlertTriangle, Cpu, Radio, CheckCircle, Clock } from 'lucide-react';

interface EmergencyReq {
  id: string;
  hospital_id: string;
  requirement: string;
  status: string;
  created_at: string;
}

export default function HospitalDashboard() {
  const { user } = useAuth();
  const [emergencies, setEmergencies] = useState<EmergencyReq[]>([]);
  const [newRequirement, setNewRequirement] = useState('');
  const [esp32Status, setEsp32Status] = useState<string>('CONNECTED');

  const fetchEmergencies = async () => {
    try {
      const res = await apiFetch<EmergencyReq[]>('/emergency');
      setEmergencies(res || []);
    } catch (err) {
      console.error('Failed to fetch emergencies', err);
    }
  };

  useEffect(() => {
    fetchEmergencies();
  }, []);

  const handleRaiseEmergency = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRequirement) return;

    try {
      await apiFetch('/emergency', {
        method: 'POST',
        body: JSON.stringify({ requirement: newRequirement }),
      });
      setNewRequirement('');
      fetchEmergencies();
    } catch (err: any) {
      alert(err.message || 'Failed to raise emergency request');
    }
  };

  const updateStatus = async (id: string, nextStatus: string) => {
    try {
      await apiFetch(`/emergency/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });
      fetchEmergencies();
    } catch (err: any) {
      alert(err.message || 'Failed to update status');
    }
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-widest">
            <Building2 className="w-4 h-4" /> Hospital Coordination Hub
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100">Emergency & Inter-Facility Network</h1>
          <p className="text-sm text-slate-400">
            Real-time emergency broadcast & hardware ESP32 sensor telemetry.
          </p>
        </div>

        {/* ESP32 Telemetry Status Badge */}
        <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-900/80 border border-slate-800">
          <Radio className="w-4 h-4 text-emerald-400 animate-ping" />
          <div>
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block">ESP32 Hardware Monitor</span>
            <span className="text-xs font-bold text-emerald-400">Node Active (Port 8899)</span>
          </div>
        </div>
      </div>

      {/* Raise Emergency Panel & List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <GlassCard glow className="space-y-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" /> Broadcast Emergency Request
          </h3>
          <p className="text-xs text-slate-400">
            Broadcast organ requirement alert across the hospital network instantly via WebSockets.
          </p>

          <form onSubmit={handleRaiseEmergency} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Emergency Organ Requirement</label>
              <textarea
                rows={3}
                required
                value={newRequirement}
                onChange={(e) => setNewRequirement(e.target.value)}
                placeholder="e.g. Critical O+ Kidney transplant required within 4 hours at ICU Unit B."
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-slate-100 text-xs focus:outline-none focus:border-amber-500"
              />
            </div>

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs shadow-lg shadow-amber-600/30 transition flex items-center justify-center gap-2"
            >
              <AlertTriangle className="w-4 h-4" /> Broadcast Emergency Alert
            </button>
          </form>
        </GlassCard>

        {/* Active Emergencies Feed */}
        <GlassCard className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-base font-bold text-slate-100">Network Emergency Feed</h3>
            <span className="text-xs font-mono text-slate-400">{emergencies.length} active alerts</span>
          </div>

          <div className="space-y-3">
            {emergencies.map((e) => (
              <div key={e.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-xs text-slate-100">{e.requirement}</h4>
                    <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1 font-mono">
                      <Clock className="w-3 h-3" /> {new Date(e.created_at).toLocaleString()}
                    </p>
                  </div>
                  <LifecycleBadge status={e.status} />
                </div>

                <div className="flex gap-2 pt-2 border-t border-slate-800">
                  {e.status === 'CREATED' && (
                    <button
                      onClick={() => updateStatus(e.id, 'ACKNOWLEDGED')}
                      className="px-3 py-1 rounded bg-indigo-600 text-white text-[11px] font-semibold"
                    >
                      Acknowledge
                    </button>
                  )}
                  {e.status === 'ACKNOWLEDGED' && (
                    <button
                      onClick={() => updateStatus(e.id, 'PROCESSING')}
                      className="px-3 py-1 rounded bg-purple-600 text-white text-[11px] font-semibold"
                    >
                      Start Processing
                    </button>
                  )}
                  {e.status === 'PROCESSING' && (
                    <button
                      onClick={() => updateStatus(e.id, 'RESOLVED')}
                      className="px-3 py-1 rounded bg-emerald-600 text-white text-[11px] font-semibold"
                    >
                      Mark Resolved
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
