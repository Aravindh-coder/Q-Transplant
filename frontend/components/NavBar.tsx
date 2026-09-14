'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '../lib/auth';
import { Activity, Cpu, LogOut, User, Shield, Stethoscope, Building2, Heart } from 'lucide-react';

export const NavBar = () => {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <nav className="glass-panel sticky top-0 z-50 px-6 py-3 border-b border-slate-800">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 shadow-lg shadow-indigo-500/30">
            <Cpu className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <span className="text-lg font-bold quantum-gradient-text tracking-wide block">
              Q-TRANSPLANT
            </span>
            <span className="text-[10px] text-indigo-400 font-medium tracking-widest block uppercase -mt-1">
              Quantum Engine v2.2
            </span>
          </div>
        </Link>

        {/* Links */}
        <div className="flex items-center gap-6">
          <Link
            href="/quantum"
            className={`flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg transition ${
              pathname === '/quantum'
                ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-4 h-4" />
            Grover Visualizer
          </Link>

          {user && (
            <>
              {user.role === 'organizer' && (
                <Link
                  href="/dashboard/organizer"
                  className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg ${
                    pathname.startsWith('/dashboard/organizer')
                      ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Shield className="w-4 h-4" />
                  Organizer Console
                </Link>
              )}

              {user.role === 'doctor' && (
                <Link
                  href="/dashboard/doctor"
                  className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg ${
                    pathname.startsWith('/dashboard/doctor')
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Stethoscope className="w-4 h-4" />
                  Doctor Workspace
                </Link>
              )}

              {user.role === 'hospital' && (
                <Link
                  href="/dashboard/hospital"
                  className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg ${
                    pathname.startsWith('/dashboard/hospital')
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Building2 className="w-4 h-4" />
                  Hospital Center
                </Link>
              )}

              {user.role === 'donor' && (
                <Link
                  href="/dashboard/donor"
                  className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg ${
                    pathname.startsWith('/dashboard/donor')
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Heart className="w-4 h-4" />
                  Donor Portal
                </Link>
              )}

              <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
                <div className="text-right">
                  <span className="text-xs font-semibold text-slate-200 block">{user.email}</span>
                  <span className="text-[10px] text-indigo-400 uppercase tracking-wider block font-mono">
                    {user.role}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-rose-500/10 transition"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          )}

          {!user && (
            <Link
              href="/"
              className="flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 transition"
            >
              <User className="w-4 h-4" />
              Sign In
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};
