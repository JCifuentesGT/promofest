import { useMemo } from 'react';
import { CatalogItem, DiscountSummary } from '../types';

/**
 * Mirrors the backend discount.service.ts logic exactly.
 * Keeping it in sync is the main trade-off of this approach —
 * noted in DECISIONS.md.
 */
export function useDiscounts(selectedItems: CatalogItem[]): DiscountSummary {
  return useMemo(() => {
    const services = selectedItems.filter(i => i.type === 'service');
    const products = selectedItems.filter(i => i.type === 'product');

    // Services
    let servicesDiscount = 0;
    if (services.length >= 2) {
      const total = services.reduce((sum, s) => sum + Number(s.price), 0);
      servicesDiscount = total > 1500 ? 5 : 3;
    }

    // Products
    let productsDiscount = 0;
    if (products.length >= 5)      productsDiscount = 5;
    else if (products.length >= 3) productsDiscount = 3;

    return { servicesDiscount, productsDiscount };
  }, [selectedItems]);
}
