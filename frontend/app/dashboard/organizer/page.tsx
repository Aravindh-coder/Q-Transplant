'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../lib/auth';
import { GlassCard } from '../../../components/GlassCard';
import { LifecycleBadge } from '../../../components/LifecycleBadge';
import { apiFetch } from '../../../lib/api';
import { Shield, UserCheck, CheckCircle2, XCircle, FileText, Activity } from 'lucide-react';

interface PendingDoctor {
  id: string;
  user_id: string;
  email?: string;
  phone: string;
  license_number: string;
  specialty: string;
  approval_status: string;
}

interface AuditLogItem {
  id: string;
  user_id: string;
  action: string;
  target?: string;
  created_at: string;
}

export default function OrganizerDashboard() {
  const { user } = useAuth();
  const [pendingDoctors, setPendingDoctors] = useState<PendingDoctor[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const docs = await apiFetch<PendingDoctor[]>('/organizer/pending-doctors');
      setPendingDoctors(docs || []);

      const logs = await apiFetch<AuditLogItem[]>('/organizer/audit-logs');
      setAuditLogs(logs || []);
    } catch (err) {
      console.error('Failed to fetch organizer data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleApprove = async (doctorId: string) => {
    try {
      await apiFetch(`/organizer/approve-doctor/${doctorId}`, { method: 'POST' });
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to approve doctor');
    }
  };

  const handleReject = async (doctorId: string) => {
    try {
      await apiFetch(`/organizer/reject-doctor/${doctorId}`, { method: 'POST' });
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to reject doctor');
    }
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-purple-400 uppercase tracking-widest">
          <Shield className="w-4 h-4" /> Organizer Command Center
        </div>
        <h1 className="text-3xl font-extrabold text-slate-100">Platform Oversight & Audit</h1>
        <p className="text-sm text-slate-400">
          Review medical practitioner licenses & monitor system-wide data security logs.
        </p>
      </div>

      {/* Doctor Approval Queue */}
      <GlassCard glow>
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-purple-400" /> Pending Doctor License Approvals
          </h3>
          <span className="text-xs font-mono text-slate-400">{pendingDoctors.length} pending review</span>
        </div>

        {pendingDoctors.length === 0 ? (
          <div className="py-8 text-center text-slate-400 text-xs bg-slate-900/30 rounded-xl border border-slate-800">
            No doctors currently awaiting authorization review.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-3">Doctor ID</th>
                  <th className="py-3 px-3">License Number</th>
                  <th className="py-3 px-3">Specialty</th>
                  <th className="py-3 px-3">Phone</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {pendingDoctors.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3 px-3 font-mono text-indigo-300">{doc.id.substring(0, 8)}...</td>
                    <td className="py-3 px-3 font-bold text-slate-100">{doc.license_number}</td>
                    <td className="py-3 px-3 text-slate-300">{doc.specialty}</td>
                    <td className="py-3 px-3 text-slate-400">{doc.phone}</td>
                    <td className="py-3 px-3">
                      <LifecycleBadge status={doc.approval_status} />
                    </td>
                    <td className="py-3 px-3 flex gap-2">
                      <button
                        onClick={() => handleApprove(doc.id)}
                        className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-1 text-[11px]"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" /> Approve
                      </button>
                      <button
                        onClick={() => handleReject(doc.id)}
                        className="px-3 py-1 rounded-lg bg-rose-600/80 hover:bg-rose-500 text-white font-semibold flex items-center gap-1 text-[11px]"
                      >
                        <XCircle className="w-3.5 h-3.5" /> Reject
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      {/* Audit Log */}
      <GlassCard>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" /> Platform Security & Access Audit Log
          </h3>
          <span className="text-xs text-slate-400 font-mono">Real-time system events</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">User ID</th>
                <th className="py-2.5 px-3">Action Executed</th>
                <th className="py-2.5 px-3">Target Resource</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-2.5 px-3 font-mono text-slate-400">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-indigo-300">
                    {log.user_id?.substring(0, 8)}...
                  </td>
                  <td className="py-2.5 px-3 font-bold text-slate-100">{log.action}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-400">{log.target || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
