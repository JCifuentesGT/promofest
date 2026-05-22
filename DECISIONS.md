# DECISIONS.md

## Decisiones técnicas relevantes

---

### Decisión 1 — Mecanismo de control de cupo bajo concurrencia

**Problema:** El formulario se distribuye por correo masivo. Es esperable una ráfaga de envíos simultáneos en los primeros minutos, especialmente al llegar a los últimos lugares disponibles. Sin un mecanismo adecuado, dos transacciones concurrentes podrían leer `confirmed_count = 49`, ambas creer que hay cupo, y ambas confirmar —superando el límite de 50.

**Opciones consideradas:**

1. **Leer y escribir sin transacción** — simple, pero produce race conditions obvias. Descartado.
2. **`SELECT ... FOR UPDATE` en PostgreSQL dentro de una transacción** — bloqueo pesimista a nivel de fila. Garantiza serialización sin coordinación externa.
3. **Contador atómico en Redis (`INCR` / `DECR`)** — más rápido bajo alta concurrencia, pero introduce un segundo sistema de estado que debe mantenerse sincronizado con la DB.

**Decisión: opción 2 — `SELECT FOR UPDATE`.**

El flujo es:
```
BEGIN
  SELECT ... FROM event_config WHERE id = 1 FOR UPDATE  ← bloquea la fila
  IF confirmed_count >= capacity → ROLLBACK + 409
  INSERT attendee
  UPDATE event_config SET confirmed_count = confirmed_count + 1
COMMIT
```

**Trade-offs aceptados:**
- Bajo carga muy alta (cientos de requests simultáneos), las transacciones hacen cola esperando el lock, lo que aumenta la latencia media. Para 50–100 asistentes esto es irrelevante.
- Si el tráfico creciera 10x (1,000+ confirmaciones concurrentes), el cuello de botella sería este lock. La migración natural sería un contador Redis con `DECR` atómico: si el resultado es ≥ 0, proceder; si es < 0, `INCR` de vuelta y rechazar. Esto elimina el lock de fila y permite escalar horizontalmente el backend.

---

### Decisión 2 — Simulación de notificación al equipo de ventas (patrón Outbox)

**Problema:** Hay que notificar al equipo de ventas tras cada confirmación. El mecanismo no debe fallar silenciosamente, no debe bloquear la respuesta al cliente, y debe ser migrable a un sistema real sin reescribir la lógica de negocio.

**Opciones consideradas:**

1. **Llamar al servicio externo dentro de la transacción** — acopla la confirmación a la disponibilidad del notificador. Si el email falla, el rollback cancelaría una confirmación válida.
2. **Cola en memoria (array/EventEmitter)** — simple, pero se pierde al reiniciar el proceso.
3. **Tabla `notification_log` + log estructurado (patrón Outbox)** — la notificación se registra en DB dentro de la misma transacción; el "envío" ocurre fuera, de forma asíncrona. Si falla, queda registro con `status='failed'` y `last_error` para reintento.

**Decisión: opción 3 — Outbox pattern.**

La notificación se persiste junto con el attendee (misma transacción en términos de datos), pero el "envío" (simulado como log estructurado con Winston) ocurre después del COMMIT y no bloquea la respuesta al cliente.

**¿Qué pasa si la notificación falla?**
El registro queda con `status='failed'`. En producción, un worker independiente podría hacer polling a `notification_log WHERE status='failed' AND attempts < 3` y reintentar. La confirmación del cliente no se ve afectada.

**¿Qué pasa si el cliente modifica su selección después de confirmar?**
No está implementado en esta versión. El diseño contempla que habría un endpoint `PATCH /api/attendees/:id` que actualizaría `attendee_items` y recalcularía descuentos, y dispararía una nueva notificación con `type: 'update'`. La notificación anterior quedaría en log como referencia histórica.

**Migración a producción:**
- Reemplazar `simulateSend()` con una llamada a SendGrid / SES / RabbitMQ.
- Añadir un worker (cron o consumer) que procese `notification_log WHERE status='pending'`.
- El resto de la lógica (outbox, reintentos, logging) se mantiene.
- Riesgo principal: duplicados si el worker reintenta una notificación que ya fue enviada pero cuyo ACK se perdió → solución: idempotency key en el notificador externo.

---

### Decisión 3 — Separación de capas en el backend (Controller → Service → Repository)

**Problema:** La prueba evalúa calidad de código y separación de responsabilidades. Una arquitectura plana (todo en el controller o en un solo archivo) sería más rápida de escribir pero dificulta el testing y el mantenimiento.

**Opciones consideradas:**

1. **Todo en el controller** — rápido, pero mezcla validación, negocio y acceso a datos.
2. **Controller + Service + Repository** — cada capa con una sola responsabilidad.
3. **Hexagonal / ports-and-adapters** — máxima separación, pero sobredimensionado para este alcance.

**Decisión: opción 2.**

- **Controller**: recibe request, valida con Zod, llama al service, devuelve response.
- **Service**: lógica de negocio pura (descuentos, orquestación de la confirmación). No sabe nada de Express ni de SQL.
- **Repository**: queries SQL. Recibe `PoolClient` cuando necesita participar en una transacción externa.

**Trade-off aceptado:** más archivos que una solución plana. El beneficio es que `discount.service.ts` es una función pura testeable sin DB ni HTTP.

---

## Situación 1 — Cupo limitado

**Mecanismo implementado:** `SELECT ... FOR UPDATE` en la tabla `event_config` (fila única con `id = 1`). Ver Decisión 1 para el razonamiento completo.

**¿Qué pasaría con 10x más tráfico?**

Con 500 requests simultáneos hacia el último lugar disponible, las transacciones harían cola en el lock de PostgreSQL. El resultado sería correcto (solo una confirma), pero la latencia del percentil 99 sería inaceptable para una experiencia web.

Pasos de escalado en orden de complejidad:
1. **Pool de conexiones más grande** — ya configurado en 20; aumentar a 50–100 con PgBouncer.
2. **Contador Redis** — `DECR` atómico antes de abrir la transacción. Si el resultado es negativo, rechazar sin tocar Postgres.
3. **Rate limiting agresivo en el API gateway** — absorber el spike antes de llegar al backend.
4. **Queue de confirmaciones** — las requests entran a una cola (SQS/RabbitMQ), se procesan secuencialmente. El cliente recibe un `202 Accepted` y consulta el estado después.

La opción 4 es la más robusta para escenarios extremos, pero cambia el contrato UX (confirmación asíncrona).

---

## Situación 2 — Notificación a ventas

Ver Decisión 2 para el diseño detallado.

**Resumen del mecanismo:** Log estructurado con Winston + registro en `notification_log`. Cada confirmación genera una entrada JSON con nombre del cliente, items seleccionados, descuentos y fecha. El equipo de ventas puede consultar los logs o la tabla directamente.

**Migración a producción:**
- Reemplazar `simulateSend()` → llamada a proveedor real (SendGrid, SES, etc.)
- Añadir worker de reintentos para `status='failed'`
- Considerar idempotency keys para evitar duplicados

---

## Limitaciones conocidas y siguientes pasos

| Limitación | Impacto a 100k usuarios | Solución |
|---|---|---|
| Lock de fila en `event_config` | Cuello de botella severo | Contador Redis atómico |
| Notificación síncrona en memoria | Se pierde si el proceso muere | Worker + cola persistente |
| JWT sin revocación | Tokens comprometidos siguen válidos | Redis allowlist o token rotation |
| Sin paginación en catálogo | OK para ~10 items; lento para miles | Cursor-based pagination |
| Sin rate limiting por IP en `/confirm` | Vulnerable a spam de confirmaciones | Rate limit granular + CAPTCHA |
| Frontend recalcula descuentos localmente | Puede desincronizarse si cambian las reglas | Endpoint `POST /api/discount/preview` |

**Lo que no implementé y reconozco:**
- Tests unitarios (el `discount.service.ts` está diseñado para ser testeable, pero no hay suite configurada).
- Refresh tokens — el JWT expira en 2h y el usuario debe volver a loguear.
- Panel de administración para ver confirmaciones y estadísticas.
