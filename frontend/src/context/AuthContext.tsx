import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { User, AuthResponse } from '../types';
import { authService } from '../services';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function loadFromStorage(): { user: User | null; token: string | null } {
  try {
    const token = localStorage.getItem('pf_token');
    const raw   = localStorage.getItem('pf_user');
    const user  = raw ? (JSON.parse(raw) as User) : null;
    return { token, user };
  } catch {
    return { token: null, user: null };
  }
}

function saveToStorage(data: AuthResponse) {
  localStorage.setItem('pf_token', data.token);
  localStorage.setItem('pf_user', JSON.stringify(data.user));
}

function clearStorage() {
  localStorage.removeItem('pf_token');
  localStorage.removeItem('pf_user');
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const stored = loadFromStorage();
  const [user,  setUser]  = useState<User | null>(stored.user);
  const [token, setToken] = useState<string | null>(stored.token);

  const handleAuth = useCallback((data: AuthResponse) => {
    saveToStorage(data);
    setToken(data.token);
    setUser(data.user);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await authService.login(email, password);
    handleAuth(data);
  }, [handleAuth]);

  const register = useCallback(async (email: string, password: string) => {
    const data = await authService.register(email, password);
    handleAuth(data);
  }, [handleAuth]);

  const logout = useCallback(() => {
    clearStorage();
    setUser(null);
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider value={{
      user, token,
      isAuthenticated: !!token,
      login, register, logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
