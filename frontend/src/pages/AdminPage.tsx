import { useState, useEffect, useMemo } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { attendeeService } from '../services';
import { useAuth } from '../context/AuthContext';
import { Attendee, AdminReport } from '../types';
import { Spinner } from '../components/ui';

// ── Helpers ────────────────────────────────────────────────────────────────────

function fmt(date: string) {
  try { return format(new Date(date), "d MMM yyyy, HH:mm", { locale: es }); }
  catch { return date; }
}

function fmtDate(date: string) {
  try { return format(new Date(date), "EEE d MMM, HH:mm", { locale: es }); }
  catch { return date; }
}

// ── Main component ─────────────────────────────────────────────────────────────

export default function AdminPage() {
  const { user, logout } = useAuth();
  const [report,  setReport]  = useState<AdminReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');
  const [search,  setSearch]  = useState('');
  const [dateFilter, setDateFilter] = useState('');

  useEffect(() => {
    attendeeService.listAll()
      .then(setReport)
      .catch(() => setError('No se pudo cargar el reporte.'))
      .finally(() => setLoading(false));
  }, []);

  // Unique attendance dates for filter dropdown
  const uniqueDates = useMemo(() => {
    if (!report) return [];
    const dates = [...new Set(
      report.attendees.map(a => a.attend_at.slice(0, 10))
    )].sort();
    return dates;
  }, [report]);

  const filtered = useMemo(() => {
    if (!report) return [];
    const q = search.toLowerCase();
    return report.attendees.filter(a => {
      const matchSearch =
        !q ||
        a.first_name.toLowerCase().includes(q) ||
        a.last_name.toLowerCase().includes(q) ||
        a.email.toLowerCase().includes(q);
      const matchDate =
        !dateFilter || a.attend_at.slice(0, 10) === dateFilter;
      return matchSearch && matchDate;
    });
  }, [report, search, dateFilter]);

  // Aggregate stats from filtered list
  const stats = useMemo(() => {
    const totalServices = filtered.reduce((s, a) => s + a.items.filter(i => i.type === 'service').length, 0);
    const totalProducts = filtered.reduce((s, a) => s + a.items.filter(i => i.type === 'product').length, 0);
    const withServiceDiscount = filtered.filter(a => Number(a.services_discount) > 0).length;
    const withProductDiscount = filtered.filter(a => Number(a.products_discount) > 0).length;
    return { totalServices, totalProducts, withServiceDiscount, withProductDiscount };
  }, [filtered]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="text-brand-400 text-xs font-medium tracking-widest uppercase">Panel de ventas</p>
            <h1 className="font-display text-2xl text-white">PromoFest — Reporte</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-500 text-sm hidden sm:block">{user?.email}</span>
            <button onClick={logout} className="text-gray-500 hover:text-gray-300 text-sm transition-colors">
              Salir
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-xl bg-red-500/10 border border-red-500/30 px-4 py-3 text-red-400 text-sm">
            {error}
          </div>
        )}

        {report && (
          <>
            {/* ── KPI cards ── */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <KpiCard
                label="Confirmados"
                value={`${report.event.confirmed_count} / ${report.event.capacity}`}
                sub={`${report.event.spots_remaining} cupos disponibles`}
                color="brand"
              />
              <KpiCard
                label="En filtro actual"
                value={String(filtered.length)}
                sub="asistentes"
                color="gray"
              />
              <KpiCard
                label="Servicios seleccionados"
                value={String(stats.totalServices)}
                sub={`${stats.withServiceDiscount} con descuento`}
                color="emerald"
              />
              <KpiCard
                label="Productos seleccionados"
                value={String(stats.totalProducts)}
                sub={`${stats.withProductDiscount} con descuento`}
                color="amber"
              />
            </div>

            {/* ── Filters ── */}
            <div className="flex flex-col sm:flex-row gap-3 mb-5">
              <div className="relative flex-1">
                <input
                  type="text"
                  placeholder="Buscar por nombre o email..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="input-field pl-10 w-full"
                />
                <svg className="absolute left-3 top-3.5 h-4 w-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <select
                value={dateFilter}
                onChange={e => setDateFilter(e.target.value)}
                className="input-field sm:w-64"
              >
                <option value="">Todas las fechas</option>
                {uniqueDates.map(d => (
                  <option key={d} value={d}>{fmtDate(d + 'T00:00:00')}</option>
                ))}
              </select>
            </div>

            {/* ── Table ── */}
            {filtered.length === 0 ? (
              <div className="card p-12 text-center text-gray-500">
                Sin resultados para los filtros aplicados.
              </div>
            ) : (
              <div className="card overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-surface-600 text-left">
                        <Th>Asistente</Th>
                        <Th>Email</Th>
                        <Th>Sesión</Th>
                        <Th>Servicios</Th>
                        <Th>Productos</Th>
                        <Th>Desc. Serv.</Th>
                        <Th>Desc. Prod.</Th>
                        <Th>Confirmado</Th>
                        <Th>Notif.</Th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtered.map(a => (
                        <AttendeeRow key={a.id} attendee={a} />
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="px-4 py-3 border-t border-surface-600 text-xs text-gray-500">
                  {filtered.length} resultado{filtered.length !== 1 ? 's' : ''}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function KpiCard({ label, value, sub, color }: {
  label: string; value: string; sub: string;
  color: 'brand' | 'gray' | 'emerald' | 'amber';
}) {
  const colors = {
    brand:   'bg-brand-500/10 border-brand-500/30 text-brand-400',
    gray:    'bg-surface-700 border-surface-600 text-gray-300',
    emerald: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
    amber:   'bg-amber-500/10 border-amber-500/30 text-amber-400',
  };
  return (
    <div className={`rounded-2xl border p-5 ${colors[color]}`}>
      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
      <p className="text-3xl font-bold">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{sub}</p>
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">
      {children}
    </th>
  );
}

function AttendeeRow({ attendee: a }: { attendee: Attendee }) {
  const services = a.items.filter(i => i.type === 'service');
  const products = a.items.filter(i => i.type === 'product');
  const sDiscount = Number(a.services_discount);
  const pDiscount = Number(a.products_discount);

  return (
    <tr className="border-b border-surface-700 hover:bg-surface-700/40 transition-colors">
      <td className="px-4 py-3 whitespace-nowrap">
        <span className="text-gray-100 font-medium">{a.first_name} {a.last_name}</span>
      </td>
      <td className="px-4 py-3 text-gray-400 whitespace-nowrap">{a.email}</td>
      <td className="px-4 py-3 text-gray-400 whitespace-nowrap capitalize">
        {fmtDate(a.attend_at)}
      </td>
      <td className="px-4 py-3">
        {services.length === 0 ? (
          <span className="text-gray-600">—</span>
        ) : (
          <ul className="space-y-0.5">
            {services.map(s => (
              <li key={s.id} className="text-gray-300 whitespace-nowrap">{s.name}</li>
            ))}
          </ul>
        )}
      </td>
      <td className="px-4 py-3">
        {products.length === 0 ? (
          <span className="text-gray-600">—</span>
        ) : (
          <ul className="space-y-0.5">
            {products.map(p => (
              <li key={p.id} className="text-gray-300 whitespace-nowrap">{p.name}</li>
            ))}
          </ul>
        )}
      </td>
      <td className="px-4 py-3 text-center">
        {sDiscount > 0
          ? <span className="text-brand-400 font-semibold">{sDiscount}%</span>
          : <span className="text-gray-600">—</span>}
      </td>
      <td className="px-4 py-3 text-center">
        {pDiscount > 0
          ? <span className="text-amber-400 font-semibold">{pDiscount}%</span>
          : <span className="text-gray-600">—</span>}
      </td>
      <td className="px-4 py-3 text-gray-500 whitespace-nowrap">{fmt(a.created_at)}</td>
      <td className="px-4 py-3 text-center">
        {a.notified_at
          ? <span className="text-emerald-400" title={fmt(a.notified_at)}>✓</span>
          : <span className="text-gray-600">—</span>}
      </td>
    </tr>
  );
}
