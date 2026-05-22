import { pool } from '../config/database';

export interface UserRow {
  id: string;
  email: string;
  password: string;
  role: 'client' | 'admin';
}

export async function findUserByEmail(email: string): Promise<UserRow | null> {
  const { rows } = await pool.query<UserRow>(
    'SELECT id, email, password, role FROM users WHERE email = $1',
    [email]
  );
  return rows[0] ?? null;
}

export async function createUser(
  email: string,
  hashedPassword: string,
  role: 'client' | 'admin' = 'client'
): Promise<UserRow> {
  const { rows } = await pool.query<UserRow>(
    `INSERT INTO users (email, password, role)
     VALUES ($1, $2, $3)
     RETURNING id, email, password, role`,
    [email, hashedPassword, role]
  );
  return rows[0];
}
