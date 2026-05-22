import { InputHTMLAttributes, forwardRef } from 'react';
import clsx from 'clsx';

// ── Input ─────────────────────────────────────────────────
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => (
    <div className="w-full">
      {label && <label className="label">{label}</label>}
      <input
        ref={ref}
        className={clsx('input-field', error && 'border-red-500 focus:border-red-500 focus:ring-red-500', className)}
        {...props}
      />
      {error && <p className="error-text">{error}</p>}
    </div>
  )
);
Input.displayName = 'Input';

// ── Spinner ───────────────────────────────────────────────
export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const s = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' }[size];
  return (
    <svg className={clsx('animate-spin text-brand-400', s)} fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

// ── Badge ─────────────────────────────────────────────────
export function Badge({ children, variant = 'default' }: {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}) {
  const styles = {
    default: 'bg-surface-600 text-gray-300',
    success: 'bg-emerald-900/40 text-emerald-400 border border-emerald-800',
    warning: 'bg-brand-900/40 text-brand-400 border border-brand-800',
    danger:  'bg-red-900/40 text-red-400 border border-red-800',
  };
  return (
    <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', styles[variant])}>
      {children}
    </span>
  );
}

// ── Alert ─────────────────────────────────────────────────
export function Alert({ message, variant = 'danger' }: {
  message: string;
  variant?: 'danger' | 'success' | 'warning';
}) {
  const styles = {
    danger:  'bg-red-900/30 border-red-800 text-red-300',
    success: 'bg-emerald-900/30 border-emerald-800 text-emerald-300',
    warning: 'bg-brand-900/30 border-brand-800 text-brand-300',
  };
  return (
    <div className={clsx('rounded-lg border px-4 py-3 text-sm', styles[variant])}>
      {message}
    </div>
  );
}

// ── CapacityBar ───────────────────────────────────────────
export function CapacityBar({ confirmed, capacity }: { confirmed: number; capacity: number }) {
  const pct = Math.min((confirmed / capacity) * 100, 100);
  const color = pct >= 90 ? 'bg-red-500' : pct >= 70 ? 'bg-brand-500' : 'bg-emerald-500';
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{confirmed} confirmados</span>
        <span>{capacity - confirmed} lugares disponibles</span>
      </div>
      <div className="h-1.5 bg-surface-600 rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-700', color)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
