'use client';

import React, { useState, useEffect } from 'react';
import { GlassCard } from '../../components/GlassCard';
import { QuantumAmplitudeChart, GroverStep } from '../../components/QuantumAmplitudeChart';
import { apiFetch } from '../../lib/api';
import { Cpu, Play, FastForward, RotateCcw, CheckCircle, BarChart2, ShieldAlert } from 'lucide-react';

interface BenchmarkItem {
  pool_size: number;
  classical_evals: number;
  quantum_evals: number;
  reduction_pct: number;
  classical_time_s: number;
  quantum_time_s: number;
  theoretical_speedup: string;
  same_optimum: boolean;
}

export default function QuantumVisualizer() {
  const [candidatesCount, setCandidatesCount] = useState<number>(64);
  const [targetIndex, setTargetIndex] = useState<number>(3);
  const [steps, setSteps] = useState<GroverStep[]>([]);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [optimalIters, setOptimalIters] = useState<number>(0);
  const [benchmarks, setBenchmarks] = useState<BenchmarkItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchSimulation = async () => {
    setLoading(true);
    try {
      const res = await apiFetch<{
        n_candidates: number;
        target_index: number;
        theoretical_optimal_iterations: number;
        steps: GroverStep[];
      }>(`/quantum/grover-sim?n_candidates=${candidatesCount}&target_index=${targetIndex}`);

      setSteps(res.steps);
      setOptimalIters(res.theoretical_optimal_iterations);
      setCurrentStep(0);
    } catch (err) {
      console.error('Failed to fetch Grover sim', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchBenchmark = async () => {
    try {
      const res = await apiFetch<{ benchmark: BenchmarkItem[] }>('/quantum/benchmark');
      setBenchmarks(res.benchmark || []);
    } catch (err) {
      console.error('Failed to fetch benchmarks', err);
    }
  };

  useEffect(() => {
    fetchSimulation();
    fetchBenchmark();
  }, [candidatesCount, targetIndex]);

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400 uppercase tracking-widest">
            <Cpu className="w-4 h-4" /> Quantum Search Engine
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100">Grover&apos;s Algorithm Visualizer</h1>
          <p className="text-sm text-slate-400">
            Phase inversion and amplitude amplification over $O(\sqrt{N})$ iterations.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentStep((s) => Math.max(0, s - 1))}
            disabled={currentStep === 0}
            className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700 disabled:opacity-40"
          >
            Previous Step
          </button>
          <span className="text-xs text-slate-400 font-mono">
            {currentStep + 1} / {steps.length || 1}
          </span>
          <button
            onClick={() => setCurrentStep((s) => Math.min(steps.length - 1, s + 1))}
            disabled={currentStep >= steps.length - 1}
            className="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 disabled:opacity-40"
          >
            Next Step
          </button>
        </div>
      </div>

      {/* Main Simulation Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="lg:col-span-2 space-y-6" glow>
          {loading ? (
            <div className="py-20 text-center text-slate-400 text-sm">Simulating Quantum State Vector...</div>
          ) : (
            <QuantumAmplitudeChart steps={steps} currentStepIndex={currentStep} />
          )}

          <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
            <div>Candidate Registry Size (N): <span className="text-slate-200 font-bold">{candidatesCount}</span></div>
            <div>Optimal Grover Steps ≈ (π/4)√N: <span className="text-indigo-400 font-bold">{optimalIters}</span></div>
            <div>Classical Search Steps (O(N)): <span className="text-rose-400 font-bold">{candidatesCount}</span></div>
          </div>
        </GlassCard>

        {/* Controls */}
        <div className="space-y-6">
          <GlassCard>
            <h3 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-indigo-400" /> Circuit Parameters
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">
                  Candidate Pool Size ($N = {candidatesCount}$)
                </label>
                <input
                  type="range"
                  min="16"
                  max="512"
                  step="16"
                  value={candidatesCount}
                  onChange={(e) => setCandidatesCount(parseInt(e.target.value))}
                  className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">
                  Target Candidate State Index ($|{targetIndex}⟩$)
                </label>
                <input
                  type="number"
                  min="0"
                  max={candidatesCount - 1}
                  value={targetIndex}
                  onChange={(e) => setTargetIndex(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300">
                Grover search amplifies probability from 1/N = {(1/candidatesCount * 100).toFixed(2)}% to near 100% in optimal iterations.
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <h3 className="text-sm font-bold text-slate-100 mb-2 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" /> Clinical Safety Notice
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Quantum matching acts as a decision support system. Final approval requires clinical crossmatching & medical evaluation by transplant teams.
            </p>
          </GlassCard>
        </div>
      </div>

      {/* Benchmark Table */}
      <GlassCard>
        <div className="mb-4">
          <h3 className="text-base font-bold text-slate-100">Quantum vs Classical Scale Benchmark</h3>
          <p className="text-xs text-slate-400">Comparing evaluation iterations across candidate pool sizes</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Pool Size (N)</th>
                <th className="py-3 px-4">Classical Evals O(N)</th>
                <th className="py-3 px-4">Quantum Evals O(√N)</th>
                <th className="py-3 px-4">Evaluation Reduction</th>
                <th className="py-3 px-4">Theoretical Speedup</th>
                <th className="py-3 px-4">Optimum Match</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {benchmarks.map((b, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 px-4 font-bold text-indigo-300">{b.pool_size}</td>
                  <td className="py-3 px-4 font-mono text-rose-400">{b.classical_evals}</td>
                  <td className="py-3 px-4 font-mono text-emerald-400 font-bold">{b.quantum_evals}</td>
                  <td className="py-3 px-4 font-bold text-emerald-300">{b.reduction_pct}%</td>
                  <td className="py-3 px-4 font-mono text-amber-400">{b.theoretical_speedup}</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-emerald-400">
                      <CheckCircle className="w-3.5 h-3.5" /> Identical
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
