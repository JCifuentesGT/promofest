import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Input } from '../components/ui';
import { StepOneData } from '../types';

const schema = z.object({
  first_name: z.string().min(1, 'Nombre requerido').max(100),
  last_name:  z.string().min(1, 'Apellido requerido').max(100),
  email:      z.string().email('Email inválido'),
  attend_at:  z.string().min(1, 'Seleccione fecha y hora'),
});

interface Props {
  defaultValues?: Partial<StepOneData>;
  /** When provided, the email field is pre-filled and locked to this value */
  lockedEmail?: string;
  onNext: (data: StepOneData) => void;
}

// Event date options for the demo (fixed dates for the fair)
const EVENT_DATES = [
  { label: 'Día 1 — Jueves 21 ago, 9:00 AM',  value: '2025-08-21T09:00:00' },
  { label: 'Día 1 — Jueves 21 ago, 2:00 PM',  value: '2025-08-21T14:00:00' },
  { label: 'Día 2 — Viernes 22 ago, 9:00 AM', value: '2025-08-22T09:00:00' },
  { label: 'Día 2 — Viernes 22 ago, 2:00 PM', value: '2025-08-22T14:00:00' },
];

export default function StepOne({ defaultValues, lockedEmail, onNext }: Props) {
  const { register, handleSubmit, formState: { errors } } =
    useForm<StepOneData>({
      resolver: zodResolver(schema),
      defaultValues: lockedEmail
        ? { ...defaultValues, email: lockedEmail }
        : defaultValues,
    });

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Nombre"
          placeholder="María"
          error={errors.first_name?.message}
          {...register('first_name')}
        />
        <Input
          label="Apellidos"
          placeholder="García López"
          error={errors.last_name?.message}
          {...register('last_name')}
        />
      </div>

      {/* Email — pre-filled & locked to the authenticated account */}
      <div className="relative">
        <Input
          label="Correo electrónico"
          type="email"
          placeholder="maria@empresa.com"
          error={errors.email?.message}
          readOnly={!!lockedEmail}
          className={lockedEmail ? 'pr-10 cursor-not-allowed opacity-70' : ''}
          {...register('email')}
        />
        {lockedEmail && (
          <span className="absolute right-3 top-9 text-gray-500 text-xs select-none" title="Correo de tu cuenta">
            🔒
          </span>
        )}
      </div>

      <div className="w-full">
        <label className="label">Fecha y hora de asistencia</label>
        <select
          className="input-field"
          {...register('attend_at')}
        >
          <option value="">Seleccione una sesión</option>
          {EVENT_DATES.map(d => (
            <option key={d.value} value={d.value}>{d.label}</option>
          ))}
        </select>
        {errors.attend_at && <p className="error-text">{errors.attend_at.message}</p>}
      </div>

      <button type="submit" className="btn-primary w-full mt-2">
        Continuar →
      </button>
    </form>
  );
}
