import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { findUserByEmail, createUser } from '../repositories/auth.repository';
import { JwtPayload } from '../types';

const JWT_SECRET = process.env.JWT_SECRET || 'changeme';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '2h';

function signToken(payload: JwtPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN } as jwt.SignOptions);
}

export async function register(email: string, password: string) {
  const existing = await findUserByEmail(email);
  if (existing) {
    throw Object.assign(new Error('El email ya está registrado'), { status: 409 });
  }

  const hashed = await bcrypt.hash(password, 12);
  const user = await createUser(email, hashed);

  const token = signToken({ userId: user.id, email: user.email, role: user.role });
  return { token, user: { id: user.id, email: user.email, role: user.role } };
}

export async function login(email: string, password: string) {
  const user = await findUserByEmail(email);
  if (!user) {
    throw Object.assign(new Error('Credenciales incorrectas'), { status: 401 });
  }

  const valid = await bcrypt.compare(password, user.password);
  if (!valid) {
    throw Object.assign(new Error('Credenciales incorrectas'), { status: 401 });
  }

  const token = signToken({ userId: user.id, email: user.email, role: user.role });
  return { token, user: { id: user.id, email: user.email, role: user.role } };
}
