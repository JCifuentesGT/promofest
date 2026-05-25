import { Attendee } from '../types';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface Props {
  attendee: Attendee;
  onLogout: () => void;
}

export default function AlreadyConfirmed({ attendee, onLogout }: Props) {
  const services = attendee.items.filter(i => i.type === 'service');
  const products = attendee.items.filter(i => i.type === 'product');

  const formattedDate = (() => {
    try {
      return format(new Date(attendee.attend_at), "EEEE d 'de' MMMM, HH:mm 'hrs'", { locale: es });
    } catch {
      return attendee.attend_at;
    }
  })();

  const formattedConfirmed = (() => {
    try {
      return format(new Date(attendee.created_at), "d 'de' MMMM yyyy, HH:mm", { locale: es });
    } catch {
      return attendee.created_at;
    }
  })();

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-amber-500/5 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-brand-500/5 blur-3xl" />
      </div>

      <div className="w-full max-w-md animate-fade-up">
        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="h-20 w-20 rounded-full bg-amber-500/15 border border-amber-500/40 flex items-center justify-center">
            <svg className="h-10 w-10 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        <div className="text-center mb-8">
          <h1 className="font-display text-3xl text-white mb-2">Ya estás confirmado</h1>
          <p className="text-gray-400 text-sm">
            Hola <span className="text-white font-medium">{attendee.first_name}</span>, tu cupo ya fue registrado
            el <span className="text-gray-300">{formattedConfirmed}</span>.
          </p>
        </div>

        <div className="card p-6 space-y-5">
          {/* Attendance date */}
          <div className="flex items-start gap-3">
            <div className="h-8 w-8 rounded-lg bg-brand-500/15 flex items-center justify-center shrink-0 mt-0.5">
              <svg className="h-4 w-4 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-0.5">Tu sesión</p>
              <p className="text-gray-200 text-sm capitalize">{formattedDate}</p>
            </div>
          </div>

          <div className="border-t border-surface-600" />

          {/* Items */}
          {services.length > 0 && (
            <ItemGroup title="Servicios seleccionados" items={services} discount={Number(attendee.services_discount)} />
          )}
          {products.length > 0 && (
            <ItemGroup title="Productos seleccionados" items={products} discount={Number(attendee.products_discount)} />
          )}

          {services.length === 0 && products.length === 0 && (
            <p className="text-xs text-gray-500 text-center py-2">Sin servicios o productos seleccionados</p>
          )}
        </div>

        <p className="text-center text-xs text-gray-500 mt-4 mb-6">
          Si necesitas modificar tu confirmación, contacta al equipo en 2223-2425.
        </p>

        <button onClick={onLogout} className="btn-secondary w-full text-sm">
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}

function ItemGroup({ title, items, discount }: {
  title: string;
  items: Array<{ id: string; name: string; price: number }>;
  discount: number;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{title}</p>
        {discount > 0 && (
          <span className="text-xs bg-brand-500/15 border border-brand-500/40 text-brand-400 px-2 py-0.5 rounded-full">
            {discount}% desc.
          </span>
        )}
      </div>
      {items.map(i => (
        <div key={i.id} className="flex justify-between text-sm">
          <span className="text-gray-300">{i.name}</span>
          <span className="text-gray-500">Q.{Number(i.price).toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
}
