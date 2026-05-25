import api from './api';
import { AdminReport, Attendee, AuthResponse, CatalogItem, ConfirmResponse, EventStatus } from '../types';

// ── Auth ─────────────────────────────────────────────────
export const authService = {
  register: (email: string, password: string) =>
    api.post<AuthResponse>('/api/auth/register', { email, password }).then(r => r.data),

  login: (email: string, password: string) =>
    api.post<AuthResponse>('/api/auth/login', { email, password }).then(r => r.data),
};

// ── Catalog ──────────────────────────────────────────────
export const catalogService = {
  getAll: () =>
    api.get<{ items: CatalogItem[] }>('/api/catalog').then(r => r.data.items),
};

// ── Event ────────────────────────────────────────────────
export const eventService = {
  getStatus: () =>
    api.get<EventStatus>('/api/attendees/event-status').then(r => r.data),
};

// ── Attendees ────────────────────────────────────────────
export const attendeeService = {
  confirm: (payload: {
    first_name: string;
    last_name: string;
    email: string;
    attend_at: string;
    item_ids: string[];
  }) =>
    api.post<ConfirmResponse>('/api/attendees/confirm', payload).then(r => r.data),

  // Returns the logged-in user's confirmation, or null if none yet
  getMyConfirmation: () =>
    api.get<{ attendee: Attendee }>('/api/attendees/me')
      .then(r => r.data.attendee)
      .catch(err => {
        if (err.response?.status === 404) return null;
        throw err;
      }),

  // Admin: full attendee list + event stats
  listAll: () =>
    api.get<AdminReport>('/api/attendees').then(r => r.data),
};
