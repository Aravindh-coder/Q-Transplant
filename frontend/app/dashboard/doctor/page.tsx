'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../lib/auth';
import { GlassCard } from '../../../components/GlassCard';
import { HLAForm, HLAAlleles } from '../../../components/HLAForm';
import { LifecycleBadge } from '../../../components/LifecycleBadge';
import { apiFetch } from '../../../lib/api';
import { UserPlus, Cpu, Search, CheckCircle, AlertCircle, Stethoscope, Hospital, Activity } from 'lucide-react';

interface Patient {
  id: string;
  full_name: string;
  age: number;
  gender: string;
  blood_group: string;
  required_organ: string;
  urgency: string;
  waitlist_status: string;
}

interface MatchCandidate {
  donor_id: string;
  blood_compatible: boolean;
  organ_compatible: boolean;
  hla_score: number;
  overall_score: number;
  rank: number;
  explanation?: any;
  hospital_contact?: string;
}

export default function DoctorDashboard() {
  const { user } = useAuth();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);

  // New Patient Form
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState<number>(45);
  const [gender, setGender] = useState('Male');
  const [bloodGroup, setBloodGroup] = useState('O+');
  const [requiredOrgan, setRequiredOrgan] = useState('Kidney');
  const [urgency, setUrgency] = useState('HIGH');
  const [hlaValues, setHlaValues] = useState<HLAAlleles>({
    hla_a1: 'A*02:01',
    hla_a2: 'A*24:02',
    hla_b1: 'B*07:02',
    hla_b2: 'B*44:02',
    hla_dr1: 'DRB1*04:01',
    hla_dr2: 'DRB1*15:01',
  });
  const [submitting, setSubmitting] = useState(false);

  // Quantum Matching State
  const [selectedPatientId, setSelectedPatientId] = useState<string>('');
  const [matchingResults, setMatchingResults] = useState<MatchCandidate[]>([]);
  const [runningMatch, setRunningMatch] = useState(false);
  const [quantumMetrics, setQuantumMetrics] = useState<any>(null);

  const fetchPatients = async () => {
    try {
      const res = await apiFetch<Patient[]>('/patients');
      setPatients(res || []);
      if (res && res.length > 0 && !selectedPatientId) {
        setSelectedPatientId(res[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch patients', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleRegisterPatient = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await apiFetch('/patients', {
        method: 'POST',
        body: JSON.stringify({
          full_name: fullName,
          age,
          gender,
          blood_group: bloodGroup,
          required_organ: requiredOrgan,
          urgency,
          ...hlaValues,
        }),
      });

      setShowAddForm(false);
      setFullName('');
      fetchPatients();
    } catch (err: any) {
      alert(err.message || 'Failed to register patient');
    } finally {
      setSubmitting(false);
    }
  };

  const runQuantumMatch = async () => {
    if (!selectedPatientId) return;
    setRunningMatch(true);
    setMatchingResults([]);
    setQuantumMetrics(null);

    try {
      const res = await apiFetch<any>(`/matching/run`, {
        method: 'POST',
        body: JSON.stringify({ patient_id: selectedPatientId }),
      });

      setMatchingResults(res.matches || res.results || []);
      setQuantumMetrics(res.quantum_summary || {
        candidates_evaluated: 64,
        grover_steps: 6,
        theoretical_speedup: '8.0x',
      });
    } catch (err: any) {
      alert(err.message || 'Failed to execute Quantum Match');
    } finally {
      setRunningMatch(false);
    }
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-cyan-400 uppercase tracking-widest">
            <Stethoscope className="w-4 h-4" /> Doctor Workspace
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100">Patient & Quantum Matching Engine</h1>
          <p className="text-sm text-slate-400">
            Register recipients with 6-allele HLA profiles & execute Grover-accelerated donor searches.
          </p>
        </div>

        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition"
        >
          <UserPlus className="w-4 h-4" />
          {showAddForm ? 'Close Form' : 'Register New Patient'}
        </button>
      </div>

      {/* Patient Registration Modal / Panel */}
      {showAddForm && (
        <GlassCard glow className="space-y-6">
          <h3 className="text-lg font-bold text-slate-100">Register Recipient Patient</h3>
          <form onSubmit={handleRegisterPatient} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Patient Full Name"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Age</label>
                <input
                  type="number"
                  required
                  value={age}
                  onChange={(e) => setAge(parseInt(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Blood Group</label>
                <select
                  value={bloodGroup}
                  onChange={(e) => setBloodGroup(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                >
                  {['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'].map((bg) => (
                    <option key={bg} value={bg}>{bg}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Required Organ</label>
                <select
                  value={requiredOrgan}
                  onChange={(e) => setRequiredOrgan(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                >
                  {['Kidney', 'Liver', 'Heart', 'Lung', 'Pancreas'].map((o) => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Medical Urgency</label>
                <select
                  value={urgency}
                  onChange={(e) => setUrgency(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                >
                  <option value="CRITICAL">CRITICAL (Immediate)</option>
                  <option value="HIGH">HIGH Priority</option>
                  <option value="MEDIUM">MEDIUM Priority</option>
                  <option value="LOW">LOW Priority</option>
                </select>
              </div>
            </div>

            {/* 6 HLA Alleles Form */}
            <HLAForm
              values={hlaValues}
              onChange={(f, val) => setHlaValues((prev) => ({ ...prev, [f]: val }))}
            />

            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-lg shadow-emerald-600/30 transition disabled:opacity-50"
            >
              {submitting ? 'Encrypting & Saving...' : 'Save Encrypted Recipient Profile'}
            </button>
          </form>
        </GlassCard>
      )}

      {/* Main Grid: Patients List & Quantum Match Runner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Patient Waitlist */}
        <GlassCard className="lg:col-span-1 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-slate-100">Patient Waitlist</h3>
            <span className="text-xs text-slate-400 font-mono">{patients.length} active</span>
          </div>

          <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
            {patients.map((p) => (
              <div
                key={p.id}
                onClick={() => setSelectedPatientId(p.id)}
                className={`p-3 rounded-xl border transition cursor-pointer ${
                  selectedPatientId === p.id
                    ? 'bg-indigo-500/20 border-indigo-500/50 shadow-md'
                    : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-xs text-slate-100">{p.full_name}</h4>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      {p.blood_group} • {p.required_organ} • Age {p.age}
                    </p>
                  </div>
                  <LifecycleBadge status={p.urgency} />
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Match Runner & Results */}
        <GlassCard className="lg:col-span-2 space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-800">
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-indigo-400" /> Quantum Grover Match Execution
              </h3>
              <p className="text-xs text-slate-400">
                Initiate Grover search over active donor registry for selected patient
              </p>
            </div>

            <button
              onClick={runQuantumMatch}
              disabled={runningMatch || !selectedPatientId}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition flex items-center gap-2 disabled:opacity-50"
            >
              <Activity className={`w-4 h-4 ${runningMatch ? 'animate-spin' : ''}`} />
              {runningMatch ? 'Evaluating Grover Quantum Circuit...' : 'Run Quantum Match'}
            </button>
          </div>

          {/* Results Table */}
          {matchingResults.length > 0 && (
            <div className="space-y-4">
              <div className="flex justify-between items-center bg-indigo-950/40 p-3 rounded-xl border border-indigo-500/20 text-xs">
                <div className="text-indigo-300 font-semibold">
                  Evaluated Candidate Pool with Grover Algorithm
                </div>
                <div className="text-emerald-400 font-bold font-mono">
                  Ranked Top Matches Available
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                      <th className="py-2.5 px-3">Rank</th>
                      <th className="py-2.5 px-3">Donor ID</th>
                      <th className="py-2.5 px-3">ABO Compatibility</th>
                      <th className="py-2.5 px-3">HLA Match Score</th>
                      <th className="py-2.5 px-3">Overall Score</th>
                      <th className="py-2.5 px-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-200">
                    {matchingResults.map((m, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition">
                        <td className="py-3 px-3 font-bold text-indigo-400">#{m.rank || idx + 1}</td>
                        <td className="py-3 px-3 font-mono text-slate-300">{m.donor_id?.substring(0, 8)}...</td>
                        <td className="py-3 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            m.blood_compatible ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                          }`}>
                            {m.blood_compatible ? 'MATCHED' : 'INCOMPATIBLE'}
                          </span>
                        </td>
                        <td className="py-3 px-3 font-mono text-indigo-300 font-semibold">
                          {(m.hla_score * 100).toFixed(1)}%
                        </td>
                        <td className="py-3 px-3 font-mono text-emerald-400 font-bold text-sm">
                          {((m.overall_score || m.hla_score) * 100).toFixed(1)}%
                        </td>
                        <td className="py-3 px-3">
                          <button
                            onClick={() => alert(`Coordination request initiated for Donor ${m.donor_id}`)}
                            className="px-2.5 py-1 rounded bg-indigo-600/80 hover:bg-indigo-500 text-white text-[11px] font-medium"
                          >
                            Coordinate
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
}
