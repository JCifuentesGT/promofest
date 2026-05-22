export type ItemType = 'service' | 'product';

export interface CatalogItem {
  id: string;
  name: string;
  description: string | null;
  price: number;
  type: ItemType;
}

export interface User {
  id: string;
  email: string;
  role: 'client' | 'admin';
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface EventStatus {
  capacity: number;
  confirmed_count: number;
  spots_remaining: number;
}

export interface Attendee {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  attend_at: string;
  services_discount: number;
  products_discount: number;
  items: CatalogItem[];
}

export interface ConfirmResponse {
  attendee: Attendee;
  discounts: {
    servicesDiscount: number;
    productsDiscount: number;
  };
}

export interface DiscountSummary {
  servicesDiscount: number;
  productsDiscount: number;
}

// Form data shape
export interface StepOneData {
  first_name: string;
  last_name: string;
  email: string;
  attend_at: string;
}
