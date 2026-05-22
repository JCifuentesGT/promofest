import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { catalogService, attendeeService, eventService } from '../services';
import { CatalogItem, ConfirmResponse, EventStatus, StepOneData } from '../types';
import StepOne from './StepOne';
import StepTwo from './StepTwo';
import ConfirmationSuccess from './ConfirmationSuccess';
import { Alert, CapacityBar, Spinner } from '../components/ui';

type Step = 1 | 2 | 'done';

export default function ConfirmPage() {
  const { user, logout } = useAuth();

  const [step,        setStep]        = useState<Step>(1);
  const [stepOneData, setStepOneData] = useState<StepOneData | null>(null);
  const [items,       setItems]       = useState<CatalogItem[]>([]);
  const [loadingItems, setLoadingItems] = useState(true);
  const [eventStatus, setEventStatus] = useState<EventStatus | null>(null);
  const [apiError,    setApiError]    = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result,      setResult]      = useState<ConfirmResponse | null>(null);

  // Load catalog and event status on mount
  useEffect(() => {
    Promise.all([
      catalogService.getAll(),
      eventService.getStatus(),
    ]).then(([catalog, status]) => {
      setItems(catalog);
      setEventStatus(status);
    }).catch(() => {
      setApiError('Error al cargar el catálogo. Recarga la página.');
    }).finally(() => setLoadingItems(false));
  }, []);

  const handleStepOne = (data: StepOneData) => {
    setStepOneData(data);
    setStep(2);
  };

  const handleConfirm = async (selectedIds: string[]) => {
    if (!stepOneData) return;
    setApiError('');
    setIsSubmitting(true);

    try {
      const response = await attendeeService.confirm({
        first_name: stepOneData.first_name,
        last_name:  stepOneData.last_name,
        email:      stepOneData.email,
        attend_at:  new Date(stepOneData.attend_at).toISOString(),
        item_ids:   selectedIds,
      });
      setResult(response);
      setStep('done');
    } catch (err: any) {
      const msg = err.response?.data?.error || 'Error al confirmar asistencia';
      setApiError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setStep(1);
    setStepOneData(null);
    setResult(null);
    setApiError('');
    // Refresh event status
    eventService.getStatus().then(setEventStatus).catch(() => null);
  };

  // Full page loading
  if (loadingItems) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  // Success screen
  if (step === 'done' && result) {
    return <ConfirmationSuccess data={result} onReset={handleReset} />;
  }

  // Event full
  const isFull = eventStatus ? eventStatus.spots_remaining <= 0 : false;

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-brand-500/5 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-brand-600/5 blur-3xl" />
      </div>

      <div className="w-full max-w-xl animate-fade-up">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="text-brand-400 text-xs font-medium tracking-widest uppercase">
              Feria de Promociones 2025
            </p>
            <h1 className="font-display text-2xl text-white">PromoFest</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-gray-500 text-sm hidden sm:block">{user?.email}</span>
            <button onClick={logout} className="text-gray-500 hover:text-gray-300 text-sm transition-colors">
              Salir
            </button>
          </div>
        </div>

        {/* Event capacity */}
        {eventStatus && (
          <div className="card p-4 mb-6">
            <CapacityBar confirmed={eventStatus.confirmed_count} capacity={eventStatus.capacity} />
          </div>
        )}

        {/* Full event banner */}
        {isFull && (
          <Alert message="El evento ha alcanzado su cupo máximo. No se aceptan más confirmaciones." variant="danger" />
        )}

        {!isFull && (
          <div className="card p-8">
            {/* Step indicator */}
            <div className="flex items-center gap-3 mb-8">
              <StepDot number={1} active={step === 1} done={step === 2} label="Tu información" />
              <div className="flex-1 h-px bg-surface-600" />
              <StepDot number={2} active={step === 2} done={false} label="Servicios y Productos" />
            </div>

            {apiError && (
              <div className="mb-5">
                <Alert message={apiError} />
              </div>
            )}

            {step === 1 && (
              <StepOne defaultValues={stepOneData ?? undefined} onNext={handleStepOne} />
            )}

            {step === 2 && (
              <StepTwo
                items={items}
                loading={loadingItems}
                onBack={() => setStep(1)}
                onConfirm={handleConfirm}
                isSubmitting={isSubmitting}
              />
            )}
          </div>
        )}

        <p className="text-center text-gray-600 text-xs mt-6">
          Atención al cliente: 2223-2425
        </p>
      </div>
    </div>
  );
}

function StepDot({ number, active, done, label }: {
  number: number; active: boolean; done: boolean; label: string;
}) {
  return (
    <div className="flex items-center gap-2">
      <div className={`
        h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 transition-all
        ${done    ? 'bg-emerald-500 text-white'  : ''}
        ${active  ? 'bg-brand-500 text-surface-900' : ''}
        ${!active && !done ? 'bg-surface-600 text-gray-400' : ''}
      `}>
        {done ? '✓' : number}
      </div>
      <span className={`text-xs hidden sm:block ${active ? 'text-white' : 'text-gray-500'}`}>
        {label}
      </span>
    </div>
  );
}
