'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../lib/auth';
import { GlassCard } from '../components/GlassCard';
import { Cpu, Shield, Zap, Lock, ArrowRight, Heart, Stethoscope, Building2, UserCheck } from 'lucide-react';

export default function Home() {
  const { login, user } = useAuth();
  const router = useRouter();

  const [role, setRole] = useState<'organizer' | 'doctor' | 'hospital' | 'donor'>('doctor');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Quick credentials pre-fill helper for demo convenience
  const fillCredentials = (r: 'organizer' | 'doctor' | 'hospital' | 'donor') => {
    setRole(r);
    if (r === 'organizer') {
      setEmail('aravindhjoshua10@gmail.com');
      setPassword('_BLAnbSitXFjiBNK84VAego8');
    } else {
      setEmail(`${r}@hospital.org`);
      setPassword('Password123!');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const loggedUser = await login(email, password);
      const targetRole = loggedUser.role || role;
      if (targetRole === 'organizer') router.push('/dashboard/organizer');
      else if (targetRole === 'doctor') router.push('/dashboard/doctor');
      else if (targetRole === 'hospital') router.push('/dashboard/hospital');
      else router.push('/dashboard/donor');
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please check details.');
    } finally {
      setLoading(false);
    }
  };

  if (user) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <GlassCard className="text-center max-w-md w-full" glow>
          <UserCheck className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-100">Welcome Back</h2>
          <p className="text-slate-400 text-sm mt-1 mb-6">
            Authenticated as <span className="text-indigo-300 font-medium">{user.email}</span> ({user.role})
          </p>
          <button
            onClick={() => {
              if (user.role === 'organizer') router.push('/dashboard/organizer');
              else if (user.role === 'doctor') router.push('/dashboard/doctor');
              else if (user.role === 'hospital') router.push('/dashboard/hospital');
              else router.push('/dashboard/donor');
            }}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 transition"
          >
            Go to Dashboard <ArrowRight className="w-4 h-4" />
          </button>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="space-y-16 py-8">
      {/* Hero */}
      <section className="text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold backdrop-blur-md">
          <Cpu className="w-4 h-4 animate-spin" />
          Quantum Grover Algorithm Simulation • Quadratic Speedup O(√N)
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-100 leading-tight">
          Secure Organ Matching with <br />
          <span className="quantum-gradient-text">Quantum Acceleration</span>
        </h1>

        <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
          Replacing traditional O(N) linear database lookups with Grover phase inversion & amplitude amplification. Guaranteed multi-hospital least-privilege security & encrypted HLA data.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto pt-4">
          <GlassCard className="text-left">
            <Zap className="w-6 h-6 text-amber-400 mb-2" />
            <h4 className="font-bold text-sm text-slate-100">O(√N) Quantum Search</h4>
            <p className="text-xs text-slate-400 mt-1">Quadratic reduction in match evaluation steps over large donor registries.</p>
          </GlassCard>

          <GlassCard className="text-left">
            <Lock className="w-6 h-6 text-indigo-400 mb-2" />
            <h4 className="font-bold text-sm text-slate-100">AES-256 HLA Encryption</h4>
            <p className="text-xs text-slate-400 mt-1">6-allele immunological profiles encrypted at rest & in transmission.</p>
          </GlassCard>

          <GlassCard className="text-left">
            <Shield className="w-6 h-6 text-emerald-400 mb-2" />
            <h4 className="font-bold text-sm text-slate-100">Strict Multi-Hospital RBAC</h4>
            <p className="text-xs text-slate-400 mt-1">Hospital data isolation with permission-gated cross-facility coordination.</p>
          </GlassCard>
        </div>
      </section>

      {/* Login & Portal Ingestion Form */}
      <section className="max-w-md mx-auto">
        <GlassCard glow>
          <div className="text-center mb-6">
            <h2 className="text-xl font-bold text-slate-100">Portal Authentication</h2>
            <p className="text-xs text-slate-400 mt-1">Select your access role to authenticate</p>
          </div>

          {/* Role selector tabs */}
          <div className="grid grid-cols-4 gap-1 p-1 bg-slate-900/80 rounded-xl mb-6 border border-slate-800">
            <button
              onClick={() => fillCredentials('doctor')}
              className={`py-2 text-xs font-semibold rounded-lg flex flex-col items-center gap-1 transition ${
                role === 'doctor' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Stethoscope className="w-3.5 h-3.5" />
              Doctor
            </button>
            <button
              onClick={() => fillCredentials('hospital')}
              className={`py-2 text-xs font-semibold rounded-lg flex flex-col items-center gap-1 transition ${
                role === 'hospital' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Building2 className="w-3.5 h-3.5" />
              Hospital
            </button>
            <button
              onClick={() => fillCredentials('organizer')}
              className={`py-2 text-xs font-semibold rounded-lg flex flex-col items-center gap-1 transition ${
                role === 'organizer' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Shield className="w-3.5 h-3.5" />
              Organizer
            </button>
            <button
              onClick={() => fillCredentials('donor')}
              className={`py-2 text-xs font-semibold rounded-lg flex flex-col items-center gap-1 transition ${
                role === 'donor' ? 'bg-rose-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Heart className="w-3.5 h-3.5" />
              Donor
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="doctor@hospital.org"
                className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-700/80 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
            >
              {loading ? 'Authenticating...' : `Sign In as ${role.toUpperCase()}`}
            </button>
          </form>

          <p className="text-[11px] text-center text-slate-500 mt-4">
            Least-privilege RBAC: Permissions verified on every API request.
          </p>
        </GlassCard>
      </section>
    </div>
  );
}
