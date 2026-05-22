import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '../context/AuthContext';
import { Input, Alert } from '../components/ui';

const schema = z.object({
  email:    z.string().email('Email inválido'),
  password: z.string().min(6, 'Mínimo 6 caracteres'),
});
type FormData = z.infer<typeof schema>;

export default function AuthPage() {
  const [mode, setMode]       = useState<'login' | 'register'>('login');
  const [apiError, setApiErr] = useState('');
  const { login, register }   = useAuth();
  const navigate              = useNavigate();

  const { register: reg, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    setApiErr('');
    try {
      if (mode === 'login') await login(data.email, data.password);
      else await register(data.email, data.password);
      navigate('/confirm');
    } catch (err: any) {
      setApiErr(err.response?.data?.error || 'Ocurrió un error, intente de nuevo');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-brand-500/5 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-brand-600/5 blur-3xl" />
      </div>

      <div className="w-full max-w-md animate-fade-up">
        {/* Header */}
        <div className="text-center mb-10">
          <p className="text-brand-400 text-sm font-medium tracking-widest uppercase mb-3">
            Feria de Promociones 2025
          </p>
          <h1 className="font-display text-4xl text-white mb-2">PromoFest</h1>
          <p className="text-gray-500 text-sm">
            {mode === 'login' ? 'Ingresa para confirmar tu asistencia' : 'Crea tu cuenta para continuar'}
          </p>
        </div>

        {/* Card */}
        <div className="card p-8">
          {/* Mode toggle */}
          <div className="flex rounded-lg bg-surface-700 p-1 mb-8">
            {(['login', 'register'] as const).map(m => (
              <button
                key={m}
                onClick={() => { setMode(m); setApiErr(''); }}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                  mode === m
                    ? 'bg-brand-500 text-surface-900'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                {m === 'login' ? 'Iniciar sesión' : 'Registrarse'}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <Input
              label="Correo electrónico"
              type="email"
              placeholder="tu@email.com"
              error={errors.email?.message}
              {...reg('email')}
            />
            <Input
              label="Contraseña"
              type="password"
              placeholder="••••••••"
              error={errors.password?.message}
              {...reg('password')}
            />

            {apiError && <Alert message={apiError} />}

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  Procesando...
                </>
              ) : mode === 'login' ? 'Ingresar' : 'Crear cuenta'}
            </button>
          </form>

          <p className="text-center text-gray-500 text-xs mt-6">
            Al continuar, aceptas participar en la Feria de Promociones 2025
          </p>
        </div>

        <p className="text-center text-gray-600 text-xs mt-6">
          Atención al cliente: 2223-2425
        </p>
      </div>
    </div>
  );
}
