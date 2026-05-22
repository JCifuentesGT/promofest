import { Pool } from 'pg';

export const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: Number(process.env.DB_PORT) || 5432,
  user: process.env.DB_USER || 'promofest',
  password: process.env.DB_PASSWORD || 'promofest_pass',
  database: process.env.DB_NAME || 'promofest_db',
  // Keep a healthy pool size — important for concurrent requests
  max: 20,
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 5_000,
});

export async function connectDB(): Promise<void> {
  const client = await pool.connect();
  client.release();
  console.log('✅ Database connected');
}
