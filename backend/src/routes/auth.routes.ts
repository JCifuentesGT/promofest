import { Router } from 'express';
import { validate } from '../middleware/validate';
import { authenticate } from '../middleware/auth';
import * as ctrl from '../controllers/auth.controller';

const router = Router();

router.post('/register', validate(ctrl.registerSchema), ctrl.register);
router.post('/login',    validate(ctrl.loginSchema),    ctrl.login);
router.get('/me',        authenticate,                  ctrl.me);

export default router;
