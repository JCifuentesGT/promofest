import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import { connectDB } from './config/database';
import { runMigrations, seedCatalog } from './config/migrations';
import { logger } from './utils/logger';

// ── Routes ───────────────────────────────────────────────
import authRouter     from './routes/auth.routes';
import catalogRouter  from './routes/catalog.routes';
import attendeeRouter from './routes/attendee.routes';

const app = express();
const PORT = Number(process.env.PORT) || 4000;

// ── Global rate limiter ──────────────────────────────────
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 min
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Demasiadas solicitudes, intente más tarde' },
});

// ── Middleware ───────────────────────────────────────────
app.use(cors({
  origin: process.env.FRONTEND_URL || '*',
  credentials: true,
}));
app.use(express.json());
app.use(limiter);

// ── Health check ─────────────────────────────────────────
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ── API Routes ───────────────────────────────────────────
app.use('/api/auth',      authRouter);
app.use('/api/catalog',   catalogRouter);
app.use('/api/attendees', attendeeRouter);

// ── 404 ──────────────────────────────────────────────────
app.use((_req, res) => {
  res.status(404).json({ error: 'Ruta no encontrada' });
});

// ── Global error handler ─────────────────────────────────
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  logger.error(err.message, { stack: err.stack });
  res.status(500).json({ error: 'Error interno del servidor' });
});

// ── Boot ─────────────────────────────────────────────────
async function bootstrap() {
  try {
    await connectDB();
    await runMigrations();
    await seedCatalog();
    app.listen(PORT, () => {
      logger.info(`🚀 Backend running on http://localhost:${PORT}`);
    });
  } catch (err) {
    logger.error('Failed to start server', { err });
    process.exit(1);
  }
}

bootstrap();
