import { CatalogItem, DiscountResult } from '../types';

/**
 * Calculates discount percentages based on selected services and products.
 *
 * Services rules:
 *   - 2+ services                        → 3%
 *   - 2+ services AND total price > 1500 → 5%
 *
 * Products rules:
 *   - 3+ products → 3%
 *   - 5+ products → 5%
 */
export function calculateDiscounts(items: CatalogItem[]): DiscountResult {
  const services = items.filter(i => i.type === 'service');
  const products = items.filter(i => i.type === 'product');

  // ── Services discount ──────────────────────────────────
  let servicesDiscount = 0;
  if (services.length >= 2) {
    const total = services.reduce((sum, s) => sum + Number(s.price), 0);
    servicesDiscount = total > 1500 ? 5 : 3;
  }

  // ── Products discount ──────────────────────────────────
  let productsDiscount = 0;
  if (products.length >= 5) {
    productsDiscount = 5;
  } else if (products.length >= 3) {
    productsDiscount = 3;
  }

  return { servicesDiscount, productsDiscount };
}
