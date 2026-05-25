import { Router } from 'express';
import { validate } from '../middleware/validate';
import { authenticate, requireAdmin } from '../middleware/auth';
import * as ctrl from '../controllers/attendee.controller';

const router = Router();

// Public
router.get('/event-status', ctrl.eventStatus);
// Authenticated (any user)
router.post('/confirm', authenticate, validate(ctrl.confirmSchema), ctrl.confirm);
router.get('/me', authenticate, ctrl.getMyConfirmation);
// Admin only
router.get('/', authenticate, requireAdmin, ctrl.listAttendees);

export default router;
