import { Request, Response } from 'express';
import { z } from 'zod';
import * as attendeeService from '../services/attendee.service';
import {
  getEventConfig,
  findAttendeeByEmail,
  getAttendeeWithItems,
  getAllAttendeesWithItems,
} from '../repositories/attendee.repository';
import { AuthRequest } from '../middleware/auth';

export const confirmSchema = z.object({
  first_name: z.string().min(1, 'Nombre requerido').max(100),
  last_name:  z.string().min(1, 'Apellido requerido').max(100),
  email:      z.string().email('Email inválido'),
  attend_at:  z.string().datetime({ message: 'Fecha/hora inválida' }),
  item_ids:   z.array(z.string().uuid()).min(1, 'Seleccione al menos un servicio o producto'),
});

// POST /api/attendees/confirm
export async function confirm(req: AuthRequest, res: Response): Promise<void> {
  try {
    const body = req.body as z.infer<typeof confirmSchema>;

    const result = await attendeeService.confirmAttendance({
      userId:    req.user?.userId,
      firstName: body.first_name,
      lastName:  body.last_name,
      email:     body.email,
      attendAt:  new Date(body.attend_at),
      itemIds:   body.item_ids,
    });

    res.status(201).json(result);
  } catch (err: any) {
    res.status(err.status || 500).json({ error: err.message });
  }
}

// GET /api/attendees/event-status
export async function eventStatus(_req: Request, res: Response): Promise<void> {
  try {
    const config = await getEventConfig();
    res.json(config);
  } catch {
    res.status(500).json({ error: 'Error al obtener estado del evento' });
  }
}

// GET /api/attendees/me  — returns logged-in user's own confirmation (if any)
export async function getMyConfirmation(req: AuthRequest, res: Response): Promise<void> {
  try {
    const email = req.user?.email;
    if (!email) { res.status(401).json({ error: 'No autenticado' }); return; }

    const attendee = await findAttendeeByEmail(email);
    if (!attendee) { res.status(404).json({ attendee: null }); return; }

    const full = await getAttendeeWithItems(attendee.id);
    res.json({ attendee: full });
  } catch {
    res.status(500).json({ error: 'Error al obtener confirmación' });
  }
}

// GET /api/attendees  — admin only: full list with stats
export async function listAttendees(_req: Request, res: Response): Promise<void> {
  try {
    const [attendees, event] = await Promise.all([
      getAllAttendeesWithItems(),
      getEventConfig(),
    ]);
    res.json({ attendees, event });
  } catch {
    res.status(500).json({ error: 'Error al listar asistentes' });
  }
}
