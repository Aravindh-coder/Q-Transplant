'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { getAuthToken, setAuthToken, clearAuthToken, apiFetch } from './api';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: 'organizer' | 'doctor' | 'hospital' | 'donor' | 'patient';
  status?: string;
  hospital_id?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  loading: true,
  login: async () => { throw new Error('Not implemented'); },
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = getAuthToken();
    if (savedToken) {
      setToken(savedToken);
      apiFetch<{ user: User }>('/auth/me')
        .then((res) => {
          setUser(res.user || (res as unknown as User));
        })
        .catch(() => {
          clearAuthToken();
          setUser(null);
          setToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<User> => {
    const res = await apiFetch<{ access_token: string; user?: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    const jwt = res.access_token;
    setAuthToken(jwt);
    setToken(jwt);

    // Fetch user details if not returned directly
    let u = res.user;
    if (!u) {
      const me = await apiFetch<{ user: User }>('/auth/me');
      u = me.user || (me as unknown as User);
    }
    setUser(u);
    return u;
  };

  const logout = () => {
    clearAuthToken();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
