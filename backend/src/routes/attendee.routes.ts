import { Router } from 'express';
import { validate } from '../middleware/validate';
import * as ctrl from '../controllers/attendee.controller';

const router = Router();

// Public endpoints
router.get('/event-status', ctrl.eventStatus);
router.post('/confirm', validate(ctrl.confirmSchema), ctrl.confirm);

export default router;
