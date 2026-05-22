import { useState, useMemo } from 'react';
import clsx from 'clsx';
import { CatalogItem } from '../types';
import { useDiscounts } from '../hooks/useDiscounts';
import { Spinner } from '../components/ui';

interface Props {
  items: CatalogItem[];
  loading: boolean;
  onBack: () => void;
  onConfirm: (selectedIds: string[]) => void;
  isSubmitting: boolean;
}

function formatPrice(price: number) {
  return `Q.${Number(price).toFixed(2)}`;
}

export default function StepTwo({ items, loading, onBack, onConfirm, isSubmitting }: Props) {
  const [search,      setSearch]      = useState('');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return items.filter(i =>
      i.name.toLowerCase().includes(q) ||
      (i.description ?? '').toLowerCase().includes(q)
    );
  }, [items, search]);

  const services = filtered.filter(i => i.type === 'service');
  const products = filtered.filter(i => i.type === 'product');

  const selectedItems = items.filter(i => selectedIds.has(i.id));
  const { servicesDiscount, productsDiscount } = useDiscounts(selectedItems);

  const toggle = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const selectedServices = selectedItems.filter(i => i.type === 'service');
  const selectedProducts = selectedItems.filter(i => i.type === 'product');

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="relative">
        <input
          type="text"
          placeholder="Buscar servicios y productos..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input-field pl-10"
        />
        <svg className="absolute left-3 top-3.5 h-4 w-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      {/* Catalog */}
      <div className="space-y-4 max-h-80 overflow-y-auto pr-1">
        {services.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-brand-400 uppercase tracking-wider mb-2">
              Servicios
            </p>
            <div className="space-y-2">
              {services.map(item => (
                <CatalogRow key={item.id} item={item} selected={selectedIds.has(item.id)} onToggle={toggle} />
              ))}
            </div>
          </div>
        )}

        {products.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Productos
            </p>
            <div className="space-y-2">
              {products.map(item => (
                <CatalogRow key={item.id} item={item} selected={selectedIds.has(item.id)} onToggle={toggle} />
              ))}
            </div>
          </div>
        )}

        {filtered.length === 0 && (
          <p className="text-center text-gray-500 py-8">Sin resultados para "{search}"</p>
        )}
      </div>

      {/* Selected summary */}
      {selectedItems.length > 0 && (
        <div className="border-t border-surface-600 pt-4 space-y-3">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Seleccionados ({selectedItems.length})
          </p>
          <div className="space-y-1">
            {selectedItems.map(i => (
              <div key={i.id} className="flex justify-between text-sm">
                <span className="text-gray-300 truncate">{i.name}</span>
                <span className="text-gray-400 ml-4 shrink-0">{formatPrice(i.price)}</span>
              </div>
            ))}
          </div>

          {/* Discount badges */}
          <div className="flex gap-3 pt-1">
            {servicesDiscount > 0 && (
              <DiscountBadge label="Servicios" pct={servicesDiscount} />
            )}
            {productsDiscount > 0 && (
              <DiscountBadge label="Productos" pct={productsDiscount} />
            )}
          </div>

          {/* Discount hints */}
          <div className="space-y-1">
            <DiscountHint
              achieved={servicesDiscount > 0}
              text={
                selectedServices.length < 2
                  ? `Agrega ${2 - selectedServices.length} servicio(s) más para 3% desc.`
                  : servicesDiscount < 5
                  ? `Total servicios > Q.1,500 para 5% desc.`
                  : '¡Máximo descuento en servicios!'
              }
            />
            <DiscountHint
              achieved={productsDiscount >= 5}
              text={
                selectedProducts.length < 3
                  ? `Agrega ${3 - selectedProducts.length} producto(s) más para 3% desc.`
                  : selectedProducts.length < 5
                  ? `Agrega ${5 - selectedProducts.length} producto(s) más para 5% desc.`
                  : '¡Máximo descuento en productos!'
              }
            />
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button onClick={onBack} className="btn-secondary flex-1" disabled={isSubmitting}>
          ← Atrás
        </button>
        <button
          onClick={() => onConfirm([...selectedIds])}
          disabled={selectedIds.size === 0 || isSubmitting}
          className="btn-primary flex-1 flex items-center justify-center gap-2"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Confirmando...
            </>
          ) : 'Confirmar asistencia →'}
        </button>
      </div>
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────

function CatalogRow({ item, selected, onToggle }: {
  item: CatalogItem;
  selected: boolean;
  onToggle: (id: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onToggle(item.id)}
      className={clsx(
        'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all duration-150',
        selected
          ? 'bg-brand-500/15 border border-brand-500/50'
          : 'bg-surface-700 border border-transparent hover:border-surface-500'
      )}
    >
      {/* Checkbox */}
      <div className={clsx(
        'h-4 w-4 rounded shrink-0 flex items-center justify-center border transition-colors',
        selected ? 'bg-brand-500 border-brand-500' : 'border-surface-400'
      )}>
        {selected && (
          <svg className="h-3 w-3 text-surface-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>

      <span className={clsx('flex-1 text-sm', selected ? 'text-white' : 'text-gray-300')}>
        {item.name}
      </span>

      <span className={clsx('text-sm font-medium shrink-0', selected ? 'text-brand-400' : 'text-gray-400')}>
        {`Q.${Number(item.price).toFixed(2)}`}
      </span>
    </button>
  );
}

function DiscountBadge({ label, pct }: { label: string; pct: number }) {
  return (
    <div className="flex-1 bg-brand-500/15 border border-brand-500/40 rounded-lg px-3 py-2 text-center">
      <p className="text-xs text-gray-400 mb-0.5">Descuento en {label}</p>
      <p className="text-brand-400 font-bold text-lg">{pct}%</p>
    </div>
  );
}

function DiscountHint({ achieved, text }: { achieved: boolean; text: string }) {
  return (
    <p className={clsx('text-xs flex items-center gap-1.5', achieved ? 'text-emerald-400' : 'text-gray-500')}>
      <span>{achieved ? '✓' : '○'}</span>
      {text}
    </p>
  );
}
