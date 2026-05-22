import { pool } from '../config/database';
import { getItemsByIds } from '../repositories/catalog.repository';
import {
  getEventConfigForUpdate,
  incrementConfirmedCount,
  createAttendee,
  linkAttendeeItems,
  getAttendeeWithItems,
  findAttendeeByEmail,
} from '../repositories/attendee.repository';
import { calculateDiscounts } from './discount.service';
import { notifySalesTeam } from './notification.service';
import { logger } from '../utils/logger';

export interface ConfirmAttendanceInput {
  userId?: string;
  firstName: string;
  lastName: string;
  email: string;
  attendAt: Date;
  itemIds: string[];
}

/**
 * Confirms attendance for a client.
 *
 * Concurrency strategy:
 *   All writes happen inside a single DB transaction with
 *   FOR UPDATE on event_config. This serializes concurrent
 *   confirmations at the DB level — only one transaction can
 *   hold the lock at a time, preventing overbooking.
 *
 *   Trade-off: under very high load this becomes a bottleneck.
 *   The DECISIONS.md explains the migration path to a Redis-based
 *   atomic counter for 10x+ traffic scenarios.
 */
export async function confirmAttendance(input: ConfirmAttendanceInput) {
  // Validate items exist before opening the transaction
  const items = await getItemsByIds(input.itemIds);
  if (items.length !== input.itemIds.length) {
    throw Object.assign(
      new Error('Uno o más productos/servicios no son válidos'),
      { status: 400 }
    );
  }

  // Check for duplicate confirmation
  const existing = await findAttendeeByEmail(input.email);
  if (existing) {
    throw Object.assign(
      new Error('Ya existe una confirmación para este email'),
      { status: 409 }
    );
  }

  // Calculate discounts (pure function — outside transaction)
  const { servicesDiscount, productsDiscount } = calculateDiscounts(items);

  const client = await pool.connect();
  let attendee;

  try {
    await client.query('BEGIN');

    // 1. Lock event_config row and read current counts
    const config = await getEventConfigForUpdate(client);

    if (config.spots_remaining <= 0) {
      await client.query('ROLLBACK');
      throw Object.assign(
        new Error('Lo sentimos, el evento ha alcanzado su cupo máximo'),
        { status: 409 }
      );
    }

    // 2. Create attendee record
    attendee = await createAttendee(client, {
      userId: input.userId,
      firstName: input.firstName,
      lastName: input.lastName,
      email: input.email,
      attendAt: input.attendAt,
      servicesDiscount,
      productsDiscount,
    });

    // 3. Link selected items
    await linkAttendeeItems(client, attendee.id, input.itemIds);

    // 4. Increment confirmed count atomically
    await incrementConfirmedCount(client);

    await client.query('COMMIT');

    logger.info('✅ Attendance confirmed', {
      attendee_id: attendee.id,
      email: input.email,
      spots_remaining: config.spots_remaining - 1,
    });
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }

  // Fetch full attendee with items for the response and notification
  const fullAttendee = await getAttendeeWithItems(attendee.id);
  if (!fullAttendee) throw new Error('Error al recuperar confirmación');

  // Notify sales team AFTER committing — failure here does not affect the confirmation
  notifySalesTeam(fullAttendee, items).catch(err => {
    logger.error('Background notification error', { error: err.message });
  });

  return {
    attendee: fullAttendee,
    discounts: { servicesDiscount, productsDiscount },
    spots_remaining: (await import('../repositories/attendee.repository'))
      .getEventConfig()
      .then(c => c.spots_remaining),
  };
}
