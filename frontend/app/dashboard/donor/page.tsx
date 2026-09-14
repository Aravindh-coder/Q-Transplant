'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../lib/auth';
import { GlassCard } from '../../../components/GlassCard';
import { HLAForm, HLAAlleles } from '../../../components/HLAForm';
import { apiFetch } from '../../../lib/api';
import { Heart, CheckCircle2, Lock, ShieldCheck } from 'lucide-react';

export default function DonorDashboard() {
  const { user } = useAuth();
  const [bloodGroup, setBloodGroup] = useState('O+');
  const [organsAvailable, setOrgansAvailable] = useState<string[]>(['Kidney']);
  const [hlaValues, setHlaValues] = useState<HLAAlleles>({
    hla_a1: 'A*02:01',
    hla_a2: 'A*24:02',
    hla_b1: 'B*07:02',
    hla_b2: 'B*44:02',
    hla_dr1: 'DRB1*04:01',
    hla_dr2: 'DRB1*15:01',
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleOrganToggle = (organ: string) => {
    setOrgansAvailable((prev) =>
      prev.includes(organ) ? prev.filter((o) => o !== organ) : [...prev, organ]
    );
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);

    try {
      await apiFetch('/donors', {
        method: 'POST',
        body: JSON.stringify({
          blood_group: bloodGroup,
          organs_available: organsAvailable,
          ...hlaValues,
        }),
      });
      setSaved(true);
    } catch (err: any) {
      alert(err.message || 'Failed to save donor profile');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 py-4 max-w-4xl mx-auto">
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-rose-400 uppercase tracking-widest">
          <Heart className="w-4 h-4" /> Donor Registry Portal
        </div>
        <h1 className="text-3xl font-extrabold text-slate-100">Organ Donation Registration</h1>
        <p className="text-sm text-slate-400">
          Your 6-allele HLA profile is encrypted with AES-256 and stored securely for quantum matching.
        </p>
      </div>

      <GlassCard glow className="space-y-6">
        {saved && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5" />
            Donor registration encrypted & saved to quantum match registry successfully!
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Blood Group</label>
              <select
                value={bloodGroup}
                onChange={(e) => setBloodGroup(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-rose-500"
              >
                {['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'].map((bg) => (
                  <option key={bg} value={bg}>{bg}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">Pledged Organs</label>
              <div className="flex flex-wrap gap-2">
                {['Kidney', 'Liver', 'Heart', 'Lung', 'Pancreas'].map((organ) => {
                  const active = organsAvailable.includes(organ);
                  return (
                    <button
                      type="button"
                      key={organ}
                      onClick={() => handleOrganToggle(organ)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${
                        active
                          ? 'bg-rose-600 text-white border-rose-500 shadow-md'
                          : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      {organ}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <HLAForm
            values={hlaValues}
            onChange={(f, val) => setHlaValues((prev) => ({ ...prev, [f]: val }))}
          />

          <div className="flex items-center justify-between pt-4 border-t border-slate-800">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400" /> AES-256 Cryptographic Payload Protection
            </div>

            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-purple-600 hover:from-rose-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-rose-600/30 transition disabled:opacity-50"
            >
              {saving ? 'Encrypting & Saving...' : 'Submit Donor Profile'}
            </button>
          </div>
        </form>
      </GlassCard>
    </div>
  );
}
