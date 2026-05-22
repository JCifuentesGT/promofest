import { pool } from '../config/database';
import { logger } from '../utils/logger';
import { Attendee, CatalogItem } from '../types';

interface NotificationPayload {
  attendee: {
    id: string;
    full_name: string;
    email: string;
    attend_at: string;
  };
  selected_items: {
    services: Array<{ name: string; price: number }>;
    products: Array<{ name: string; price: number }>;
  };
  discounts: {
    services: number;
    products: number;
  };
  confirmed_at: string;
}

/**
 * Persists a notification record and emits a structured log that represents
 * the "message" sent to the sales team.
 *
 * In a real production environment this would:
 *   1. Publish to a message queue (SQS, RabbitMQ, etc.)
 *   2. Or call a transactional email provider (SendGrid, Postmark, etc.)
 *
 * The DB log acts as an outbox pattern — guaranteeing at-least-once delivery
 * and enabling retries if the downstream system is unavailable.
 */
export async function notifySalesTeam(
  attendee: Attendee,
  items: CatalogItem[]
): Promise<void> {
  const payload: NotificationPayload = {
    attendee: {
      id: attendee.id,
      full_name: `${attendee.first_name} ${attendee.last_name}`,
      email: attendee.email,
      attend_at: attendee.attend_at,
    },
    selected_items: {
      services: items
        .filter(i => i.type === 'service')
        .map(i => ({ name: i.name, price: Number(i.price) })),
      products: items
        .filter(i => i.type === 'product')
        .map(i => ({ name: i.name, price: Number(i.price) })),
    },
    discounts: {
      services: attendee.services_discount,
      products: attendee.products_discount,
    },
    confirmed_at: new Date().toISOString(),
  };

  // Insert notification record (outbox pattern)
  const { rows } = await pool.query(
    `INSERT INTO notification_log (attendee_id, payload, status)
     VALUES ($1, $2, 'pending')
     RETURNING id`,
    [attendee.id, JSON.stringify(payload)]
  );

  try {
    // Simulate sending — in production: call queue/email provider here
    await simulateSend(payload);

    await pool.query(
      `UPDATE notification_log
       SET status = 'sent', sent_at = now(), attempts = attempts + 1
       WHERE id = $1`,
      [rows[0].id]
    );

    await pool.query(
      `UPDATE attendees SET notified_at = now() WHERE id = $1`,
      [attendee.id]
    );

    logger.info('📨 Sales notification sent', {
      notification_id: rows[0].id,
      attendee_id: attendee.id,
      attendee_email: attendee.email,
    });
  } catch (err: any) {
    // Notification failure must NOT roll back the confirmation
    await pool.query(
      `UPDATE notification_log
       SET status = 'failed', attempts = attempts + 1, last_error = $1
       WHERE id = $2`,
      [err.message, rows[0].id]
    );

    logger.error('❌ Sales notification failed — will require manual retry', {
      notification_id: rows[0].id,
      attendee_id: attendee.id,
      error: err.message,
    });
  }
}

/**
 * Simulates the actual send. Replace with real integration.
 * Intentionally async to mimic network latency.
 */
async function simulateSend(payload: NotificationPayload): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 50)); // simulate ~50ms latency

  // Structured log = the "notification" visible in server logs / monitoring
  logger.info('🔔 [SALES NOTIFICATION]', {
    to: 'sales-team@promofest.com',
    subject: `Nueva confirmación: ${payload.attendee.full_name}`,
    body: payload,
  });
}
