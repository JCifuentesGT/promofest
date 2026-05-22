// ── Catalog ─────────────────────────────────────────────
export type ItemType = 'service' | 'product';

export interface CatalogItem {
  id: string;
  name: string;
  description: string | null;
  price: number;
  type: ItemType;
  active: boolean;
  created_at: string;
}

// ── Attendee ─────────────────────────────────────────────
export interface Attendee {
  id: string;
  user_id: string | null;
  first_name: string;
  last_name: string;
  email: string;
  attend_at: string;
  services_discount: number;
  products_discount: number;
  status: 'confirmed' | 'cancelled';
  notified_at: string | null;
  created_at: string;
  items?: CatalogItem[];
}

// ── Discount result ──────────────────────────────────────
export interface DiscountResult {
  servicesDiscount: number;  // percentage, e.g. 5 = 5%
  productsDiscount: number;
}

// ── Event capacity ───────────────────────────────────────
export interface EventConfig {
  capacity: number;
  confirmed_count: number;
  spots_remaining: number;
}

// ── Notification ─────────────────────────────────────────
export type NotificationStatus = 'pending' | 'sent' | 'failed';

export interface NotificationLog {
  id: string;
  attendee_id: string;
  payload: Record<string, unknown>;
  status: NotificationStatus;
  attempts: number;
  last_error: string | null;
  created_at: string;
  sent_at: string | null;
}

// ── JWT payload ──────────────────────────────────────────
export interface JwtPayload {
  userId: string;
  email: string;
  role: 'client' | 'admin';
}
