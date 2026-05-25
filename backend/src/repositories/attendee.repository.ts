import { PoolClient } from 'pg';
import { pool } from '../config/database';
import { Attendee, CatalogItem, EventConfig } from '../types';

// ── Event capacity ────────────────────────────────────────────────────────────

/**
 * Reads event config WITH a row-level lock.
 * Must be called inside an open transaction.
 *
 * FOR UPDATE locks the row so concurrent transactions must wait —
 * this is the core mechanism that prevents overbooking.
 */
export async function getEventConfigForUpdate(client: PoolClient): Promise<EventConfig> {
  const { rows } = await client.query(
    `SELECT capacity, confirmed_count
     FROM event_config
     WHERE id = 1
     FOR UPDATE`
  );
  const row = rows[0];
  return {
    capacity: row.capacity,
    confirmed_count: row.confirmed_count,
    spots_remaining: row.capacity - row.confirmed_count,
  };
}

export async function incrementConfirmedCount(client: PoolClient): Promise<void> {
  await client.query(
    `UPDATE event_config
     SET confirmed_count = confirmed_count + 1
     WHERE id = 1`
  );
}

/** Public read — no lock needed */
export async function getEventConfig(): Promise<EventConfig> {
  const { rows } = await pool.query(
    `SELECT capacity, confirmed_count FROM event_config WHERE id = 1`
  );
  const row = rows[0];
  return {
    capacity: row.capacity,
    confirmed_count: row.confirmed_count,
    spots_remaining: row.capacity - row.confirmed_count,
  };
}

// ── Attendees ─────────────────────────────────────────────────────────────────

export async function findAttendeeByEmail(email: string): Promise<Attendee | null> {
  const { rows } = await pool.query<Attendee>(
    `SELECT * FROM attendees WHERE email = $1 AND status = 'confirmed'`,
    [email]
  );
  return rows[0] ?? null;
}

export interface CreateAttendeeInput {
  userId?: string;
  firstName: string;
  lastName: string;
  email: string;
  attendAt: Date;
  servicesDiscount: number;
  productsDiscount: number;
}

export async function createAttendee(
  client: PoolClient,
  input: CreateAttendeeInput
): Promise<Attendee> {
  const { rows } = await client.query<Attendee>(
    `INSERT INTO attendees
       (user_id, first_name, last_name, email, attend_at, services_discount, products_discount)
     VALUES ($1, $2, $3, $4, $5, $6, $7)
     RETURNING *`,
    [
      input.userId ?? null,
      input.firstName,
      input.lastName,
      input.email,
      input.attendAt,
      input.servicesDiscount,
      input.productsDiscount,
    ]
  );
  return rows[0];
}

export async function linkAttendeeItems(
  client: PoolClient,
  attendeeId: string,
  itemIds: string[]
): Promise<void> {
  if (itemIds.length === 0) return;
  const values = itemIds
    .map((id, i) => `($1, $${i + 2})`)
    .join(', ');
  await client.query(
    `INSERT INTO attendee_items (attendee_id, item_id) VALUES ${values}`,
    [attendeeId, ...itemIds]
  );
}

export async function getAttendeeWithItems(attendeeId: string): Promise<Attendee | null> {
  const { rows: attendeeRows } = await pool.query<Attendee>(
    'SELECT * FROM attendees WHERE id = $1',
    [attendeeId]
  );
  if (!attendeeRows[0]) return null;

  const { rows: itemRows } = await pool.query<CatalogItem>(
    `SELECT ci.* FROM catalog_items ci
     JOIN attendee_items ai ON ai.item_id = ci.id
     WHERE ai.attendee_id = $1`,
    [attendeeId]
  );

  return { ...attendeeRows[0], items: itemRows };
}

/** Admin: all confirmed attendees with their items, ordered newest first */
export async function getAllAttendeesWithItems(): Promise<Attendee[]> {
  const { rows } = await pool.query<Attendee & { items_json: CatalogItem[] | null }>(
    `SELECT
       a.*,
       json_agg(
         json_build_object(
           'id',          ci.id,
           'name',        ci.name,
           'type',        ci.type,
           'price',       ci.price,
           'description', ci.description,
           'active',      ci.active,
           'created_at',  ci.created_at
         ) ORDER BY ci.type, ci.name
       ) FILTER (WHERE ci.id IS NOT NULL) AS items_json
     FROM attendees a
     LEFT JOIN attendee_items ai ON ai.attendee_id = a.id
     LEFT JOIN catalog_items  ci ON ci.id = ai.item_id
     WHERE a.status = 'confirmed'
     GROUP BY a.id
     ORDER BY a.created_at DESC`
  );

  return rows.map(({ items_json, ...row }) => ({
    ...row,
    items: items_json ?? [],
  }));
}
