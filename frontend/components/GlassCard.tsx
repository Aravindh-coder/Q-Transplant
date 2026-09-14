import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', glow = false }) => {
  return (
    <div className={`glass-card rounded-2xl p-6 relative overflow-hidden ${glow ? 'quantum-glow' : ''} ${className}`}>
      {glow && (
        <div className="absolute -top-10 -right-10 w-32 h-32 bg-indigo-500/20 rounded-full blur-2xl pointer-events-none" />
      )}
      {children}
    </div>
  );
};
