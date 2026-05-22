import { Router, Request, Response } from 'express';
import { getAllItems } from '../repositories/catalog.repository';
import { ItemType } from '../types';

const router = Router();

// GET /api/catalog?type=service|product
router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const type = req.query.type as ItemType | undefined;
    if (type && type !== 'service' && type !== 'product') {
      res.status(400).json({ error: 'type debe ser "service" o "product"' });
      return;
    }
    const items = await getAllItems(type);
    res.json({ items });
  } catch {
    res.status(500).json({ error: 'Error al obtener catálogo' });
  }
});

export default router;
