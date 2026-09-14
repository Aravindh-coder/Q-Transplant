import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '../lib/auth';
import { NavBar } from '../components/NavBar';

export const metadata: Metadata = {
  title: 'Q-Transplant Quantum — Organ Matching & Hospital Coordination',
  description: 'Quantum-accelerated organ matching platform with Grover search O(√N) speedup and multi-hospital RBAC.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-indigo-500 selection:text-white">
        <AuthProvider>
          <div className="min-h-screen flex flex-col">
            <NavBar />
            <main className="flex-1 max-w-7xl w-full mx-auto p-6">{children}</main>
            <footer className="py-6 border-t border-slate-900 text-center text-xs text-slate-500">
              <p>Q-Transplant Quantum Architecture • Clinical Decision Support • Decision approval by authorized transplant teams</p>
            </footer>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
