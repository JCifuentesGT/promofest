import { Request, Response } from 'express';
import { z } from 'zod';
import * as authService from '../services/auth.service';

export const registerSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Mínimo 6 caracteres'),
});

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

export async function register(req: Request, res: Response): Promise<void> {
  try {
    const result = await authService.register(req.body.email, req.body.password);
    res.status(201).json(result);
  } catch (err: any) {
    res.status(err.status || 500).json({ error: err.message });
  }
}

export async function login(req: Request, res: Response): Promise<void> {
  try {
    const result = await authService.login(req.body.email, req.body.password);
    res.json(result);
  } catch (err: any) {
    res.status(err.status || 500).json({ error: err.message });
  }
}

export async function me(req: Request, res: Response): Promise<void> {
  // req.user is populated by authenticate middleware
  res.json({ user: (req as any).user });
}
