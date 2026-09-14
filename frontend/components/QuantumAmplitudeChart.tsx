'use client';

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export interface GroverStep {
  iteration: number;
  phase: string;
  description: string;
  amplitudes: number[];
  target_amplitude: number;
  target_probability: number;
  mean_amplitude: number;
}

interface Props {
  steps: GroverStep[];
  currentStepIndex: number;
}

export const QuantumAmplitudeChart: React.FC<Props> = ({ steps, currentStepIndex }) => {
  if (!steps || steps.length === 0) return null;

  const currentStep = steps[Math.min(currentStepIndex, steps.length - 1)];
  const data = (currentStep?.amplitudes || []).map((amp, idx) => ({
    state: `|${idx}⟩`,
    amplitude: parseFloat(amp.toFixed(4)),
    probability: parseFloat((amp * amp).toFixed(4)),
    isTarget: idx === 3, // Target candidate highlighted
  }));

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center bg-slate-900/60 p-4 rounded-xl border border-indigo-500/30">
        <div>
          <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Phase</span>
          <h3 className="text-base font-bold text-slate-100">{currentStep?.phase}</h3>
          <p className="text-xs text-slate-400 mt-0.5">{currentStep?.description}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-slate-400 block">Target Probability</span>
          <span className="text-xl font-bold text-emerald-400">
            {((currentStep?.target_probability || 0) * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="h-64 w-full bg-slate-950/40 p-4 rounded-xl border border-slate-800">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="state" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} domain={[-1, 1]} />
            <Tooltip
              contentStyle={{ background: '#0f172a', borderColor: '#475569', borderRadius: '8px', color: '#f8fafc' }}
            />
            <Bar dataKey="amplitude" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.amplitude < 0 ? '#ef4444' : entry.isTarget ? '#10b981' : '#6366f1'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
