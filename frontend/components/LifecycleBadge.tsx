import React from 'react';

const STATUS_MAP: Record<string, { label: string; bg: string; text: string; border: string }> = {
  'CREATED': { label: 'Created', bg: 'bg-slate-500/20', text: 'text-slate-300', border: 'border-slate-500/30' },
  'POTENTIAL_MATCH': { label: 'Potential Match', bg: 'bg-blue-500/20', text: 'text-blue-300', border: 'border-blue-500/30' },
  'UNDER_REVIEW': { label: 'Under Review', bg: 'bg-amber-500/20', text: 'text-amber-300', border: 'border-amber-500/30' },
  'HOSPITAL_COORDINATION': { label: 'Hospital Coordination', bg: 'bg-purple-500/20', text: 'text-purple-300', border: 'border-purple-500/30' },
  'MEDICAL_EVALUATION': { label: 'Medical Evaluation', bg: 'bg-cyan-500/20', text: 'text-cyan-300', border: 'border-cyan-500/30' },
  'APPROVED': { label: 'Approved', bg: 'bg-emerald-500/20', text: 'text-emerald-300', border: 'border-emerald-500/30' },
  'REJECTED': { label: 'Rejected', bg: 'bg-rose-500/20', text: 'text-rose-300', border: 'border-rose-500/30' },
  'TRANSPLANT_SCHEDULED': { label: 'Transplant Scheduled', bg: 'bg-indigo-500/20', text: 'text-indigo-300', border: 'border-indigo-500/30' },
  'PENDING_APPROVAL': { label: 'Pending Approval', bg: 'bg-amber-500/20', text: 'text-amber-300', border: 'border-amber-500/30' },
  'RESOLVED': { label: 'Resolved', bg: 'bg-emerald-500/20', text: 'text-emerald-300', border: 'border-emerald-500/30' },
};

export const LifecycleBadge: React.FC<{ status: string }> = ({ status }) => {
  const conf = STATUS_MAP[status.toUpperCase()] || {
    label: status,
    bg: 'bg-slate-500/20',
    text: 'text-slate-300',
    border: 'border-slate-500/30',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${conf.bg} ${conf.text} ${conf.border} backdrop-blur-md inline-flex items-center gap-1.5`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
      {conf.label}
    </span>
  );
};
