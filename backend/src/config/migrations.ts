import bcrypt from 'bcryptjs';
import { pool } from './database';

export async function runMigrations(): Promise<void> {
  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    // ── Users (session management) ──────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email       TEXT UNIQUE NOT NULL,
        password    TEXT NOT NULL,
        role        TEXT NOT NULL DEFAULT 'client',  -- 'client' | 'admin'
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
      );
    `);

    // ── Catalog ─────────────────────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS catalog_items (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name        TEXT NOT NULL,
        description TEXT,
        price       NUMERIC(10,2) NOT NULL,
        type        TEXT NOT NULL,   -- 'service' | 'product'
        active      BOOLEAN NOT NULL DEFAULT true,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
      );
    `);

    // ── Event config (single-row table) ─────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS event_config (
        id            INT PRIMARY KEY DEFAULT 1,
        capacity      INT NOT NULL DEFAULT 50,
        confirmed_count INT NOT NULL DEFAULT 0,
        CHECK (id = 1)   -- enforce single row
      );
    `);

    // Ensure the single row exists
    await client.query(`
      INSERT INTO event_config (id, capacity, confirmed_count)
      VALUES (1, $1, 0)
      ON CONFLICT (id) DO NOTHING;
    `, [process.env.EVENT_CAPACITY || 50]);

    // ── Attendees (confirmations) ────────────────────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS attendees (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id       UUID REFERENCES users(id),
        first_name    TEXT NOT NULL,
        last_name     TEXT NOT NULL,
        email         TEXT NOT NULL,
        attend_at     TIMESTAMPTZ NOT NULL,
        services_discount  NUMERIC(5,2) NOT NULL DEFAULT 0,
        products_discount  NUMERIC(5,2) NOT NULL DEFAULT 0,
        status        TEXT NOT NULL DEFAULT 'confirmed',  -- 'confirmed' | 'cancelled'
        notified_at   TIMESTAMPTZ,   -- when sales team was notified
        created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
      );
    `);

    // ── Attendee ↔ Catalog items (many-to-many) ──────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS attendee_items (
        attendee_id  UUID REFERENCES attendees(id) ON DELETE CASCADE,
        item_id      UUID REFERENCES catalog_items(id),
        PRIMARY KEY (attendee_id, item_id)
      );
    `);

    // ── Notification log (simulated sales queue) ─────────────
    await client.query(`
      CREATE TABLE IF NOT EXISTS notification_log (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        attendee_id   UUID REFERENCES attendees(id),
        payload       JSONB NOT NULL,
        status        TEXT NOT NULL DEFAULT 'pending',  -- 'pending' | 'sent' | 'failed'
        attempts      INT NOT NULL DEFAULT 0,
        last_error    TEXT,
        created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
        sent_at       TIMESTAMPTZ
      );
    `);

    await client.query('COMMIT');
    console.log('✅ Migrations complete');
  } catch (err) {
    await client.query('ROLLBACK');
    console.error('❌ Migration failed:', err);
    throw err;
  } finally {
    client.release();
  }
}

/**
 * Creates the admin user defined in ADMIN_EMAIL / ADMIN_PASSWORD env vars.
 * Only runs when those vars are set AND no admin user exists yet.
 * Safe to run on every boot — idempotent.
 */
export async function seedAdminUser(): Promise<void> {
  const email    = process.env.ADMIN_EMAIL;
  const password = process.env.ADMIN_PASSWORD;
  if (!email || !password) return;  // admin seeding not configured

  // Always upsert — guarantees role='admin' even if the user previously
  // registered as 'client' through the normal sign-up flow.
  const hashed = await bcrypt.hash(password, 12);
  const { rows } = await pool.query(
    `INSERT INTO users (email, password, role)
     VALUES ($1, $2, 'admin')
     ON CONFLICT (email) DO UPDATE SET role = 'admin', password = EXCLUDED.password
     RETURNING email, role`,
    [email, hashed]
  );
  console.log(`✅ Admin user ready: ${rows[0].email} (role: ${rows[0].role})`);
}

export async function seedCatalog(): Promise<void> {
  const client = await pool.connect();
  try {
    const { rows } = await client.query('SELECT COUNT(*) FROM catalog_items');
    if (Number(rows[0].count) > 0) return; // already seeded

    await client.query(`
      INSERT INTO catalog_items (name, description, price, type) VALUES
        -- Services
        ('Consultoría Estratégica',  'Sesión personalizada de consultoría de negocios', 800.00,  'service'),
        ('Soporte Premium',          'Soporte técnico prioritario 24/7',                 950.00,  'service'),
        ('Capacitación Corporativa', 'Taller de capacitación para equipos',             1200.00,  'service'),
        ('Auditoría de Procesos',    'Revisión y optimización de procesos internos',     750.00,  'service'),
        -- Products
        ('Licencia Software Pro',    'Licencia anual plataforma de gestión',             499.99,  'product'),
        ('Kit de Bienvenida',        'Set de artículos corporativos de alta calidad',     89.99,  'product'),
        ('Módulo Reportes',          'Módulo adicional de reportería avanzada',          199.99,  'product'),
        ('Módulo Integraciones',     'Conexión con sistemas de terceros',                299.99,  'product'),
        ('Manual Técnico',           'Documentación técnica impresa y digital',           49.99,  'product'),
        ('Soporte Extendido Pack',   'Pack de horas de soporte adicionales',             149.99,  'product');
    `);
    console.log('✅ Catalog seeded');
  } finally {
    client.release();
  }
}
