# PromoFest — Referencia de API

**Base URL (producción):** `https://<backend-service>.railway.app`  
**Base URL (local):** `http://localhost:4000`

Todos los endpoints retornan `Content-Type: application/json`.  
Los errores siguen el formato: `{ "error": "Mensaje descriptivo" }`.

---

## Autenticación

La API usa **JWT Bearer tokens**. Los endpoints protegidos requieren el header:

```
Authorization: Bearer <token>
```

Los tokens se obtienen en `/api/auth/login` o `/api/auth/register` y expiran según `JWT_EXPIRES_IN` (default `2h`).

---

## Rate Limiting

Todas las rutas están sujetas a un límite global de **100 solicitudes por IP cada 15 minutos**. Al superarlo, la API responde:

```json
HTTP 429 Too Many Requests
{ "error": "Demasiadas solicitudes, intente más tarde" }
```

---

## Endpoints de Autenticación — `/api/auth`

### `POST /api/auth/register`

Registra un nuevo usuario con rol `client`.

**Body:**
```json
{
  "email": "usuario@empresa.com",
  "password": "minimo6chars"
}
```

**Respuesta exitosa — `201 Created`:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "a1b2c3d4-...",
    "email": "usuario@empresa.com",
    "role": "client"
  }
}
```

**Errores:**

| Código | Descripción |
|---|---|
| `400` | Email o contraseña inválidos (falla validación Zod) |
| `409` | El email ya está registrado |

---

### `POST /api/auth/login`

Autentica un usuario existente.

**Body:**
```json
{
  "email": "usuario@empresa.com",
  "password": "mipassword"
}
```

**Respuesta exitosa — `200 OK`:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "a1b2c3d4-...",
    "email": "usuario@empresa.com",
    "role": "client"
  }
}
```

> Para usuarios admin, `"role": "admin"`.

**Errores:**

| Código | Descripción |
|---|---|
| `400` | Datos inválidos |
| `401` | Credenciales incorrectas |

---

### `GET /api/auth/me`

Retorna los datos del usuario autenticado. Requiere JWT válido.

**Headers:** `Authorization: Bearer <token>`

**Respuesta exitosa — `200 OK`:**
```json
{
  "user": {
    "userId": "a1b2c3d4-...",
    "email": "usuario@empresa.com",
    "role": "client"
  }
}
```

---

## Endpoints de Catálogo — `/api/catalog`

### `GET /api/catalog`

Retorna todos los ítems activos del catálogo (servicios y productos).

**Acceso:** Público (sin autenticación).

**Respuesta exitosa — `200 OK`:**
```json
[
  {
    "id": "uuid-1",
    "name": "Consultoría Estratégica",
    "description": "Sesión personalizada de consultoría de negocios",
    "price": "800.00",
    "type": "service",
    "active": true,
    "created_at": "2025-01-01T00:00:00.000Z"
  },
  {
    "id": "uuid-2",
    "name": "Licencia Software Pro",
    "description": "Licencia anual plataforma de gestión",
    "price": "499.99",
    "type": "product",
    "active": true,
    "created_at": "2025-01-01T00:00:00.000Z"
  }
]
```

---

## Endpoints de Asistentes — `/api/attendees`

### `GET /api/attendees/event-status`

Retorna el estado de capacidad actual del evento.

**Acceso:** Público (sin autenticación).

**Respuesta exitosa — `200 OK`:**
```json
{
  "capacity": 50,
  "confirmed_count": 23,
  "spots_remaining": 27
}
```

---

### `GET /api/attendees/me`

Retorna la confirmación existente del usuario autenticado, si existe.

**Acceso:** Requiere JWT válido (`client` o `admin`).

**Headers:** `Authorization: Bearer <token>`

**Respuesta exitosa (confirmación existente) — `200 OK`:**
```json
{
  "attendee": {
    "id": "uuid-attendee",
    "user_id": "uuid-user",
    "first_name": "María",
    "last_name": "García",
    "email": "maria@empresa.com",
    "attend_at": "2025-08-21T09:00:00.000Z",
    "services_discount": "5.00",
    "products_discount": "3.00",
    "status": "confirmed",
    "notified_at": "2025-07-10T14:30:00.000Z",
    "created_at": "2025-07-10T14:29:55.000Z",
    "items": [
      {
        "id": "uuid-item",
        "name": "Consultoría Estratégica",
        "type": "service",
        "price": "800.00",
        "description": "...",
        "active": true,
        "created_at": "..."
      }
    ]
  }
}
```

**Respuesta (sin confirmación) — `404 Not Found`:**
```json
{ "attendee": null }
```

---

### `POST /api/attendees/confirm`

Confirma la asistencia de un cliente al evento.

**Acceso:** Requiere JWT válido (`client` o `admin`).

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "first_name": "María",
  "last_name": "García López",
  "email": "maria@empresa.com",
  "attend_at": "2025-08-21T09:00:00.000Z",
  "item_ids": [
    "uuid-item-1",
    "uuid-item-2"
  ]
}
```

| Campo | Tipo | Validación |
|---|---|---|
| `first_name` | string | 1–100 caracteres |
| `last_name` | string | 1–100 caracteres |
| `email` | string | Formato email válido |
| `attend_at` | string | ISO 8601 datetime |
| `item_ids` | string[] | Al menos 1 UUID válido |

**Respuesta exitosa — `201 Created`:**
```json
{
  "attendee": {
    "id": "uuid-attendee",
    "first_name": "María",
    "last_name": "García López",
    "email": "maria@empresa.com",
    "attend_at": "2025-08-21T09:00:00.000Z",
    "services_discount": "5.00",
    "products_discount": "0.00",
    "status": "confirmed",
    "notified_at": null,
    "created_at": "2025-07-10T14:29:55.000Z",
    "items": [ ... ]
  },
  "discounts": {
    "servicesDiscount": 5,
    "productsDiscount": 0
  },
  "spots_remaining": 26
}
```

**Errores:**

| Código | Descripción |
|---|---|
| `400` | Datos inválidos o ítems no encontrados |
| `401` | Sin token o token expirado |
| `409` | Ya existe confirmación para este email |
| `409` | El evento ha alcanzado su cupo máximo |

---

### `GET /api/attendees`

Retorna todos los asistentes confirmados con sus ítems y estadísticas del evento.

**Acceso:** Requiere JWT con `role = 'admin'`.

**Headers:** `Authorization: Bearer <token>`

**Respuesta exitosa — `200 OK`:**
```json
{
  "attendees": [
    {
      "id": "uuid-attendee",
      "first_name": "María",
      "last_name": "García",
      "email": "maria@empresa.com",
      "attend_at": "2025-08-21T09:00:00.000Z",
      "services_discount": "5.00",
      "products_discount": "3.00",
      "status": "confirmed",
      "notified_at": "2025-07-10T14:30:00.000Z",
      "created_at": "2025-07-10T14:29:55.000Z",
      "items": [
        {
          "id": "uuid-item",
          "name": "Consultoría Estratégica",
          "type": "service",
          "price": "800.00",
          "description": "...",
          "active": true,
          "created_at": "..."
        }
      ]
    }
  ],
  "event": {
    "capacity": 50,
    "confirmed_count": 24,
    "spots_remaining": 26
  }
}
```

**Errores:**

| Código | Descripción |
|---|---|
| `401` | Sin token o token expirado |
| `403` | El usuario no tiene rol `admin` |

---

## Health Check

### `GET /health`

Verifica que el servidor está operativo.

**Acceso:** Público.

**Respuesta — `200 OK`:**
```json
{
  "status": "ok",
  "timestamp": "2025-07-10T14:00:00.000Z"
}
```

---

## Códigos de error comunes

| Código HTTP | Significado |
|---|---|
| `400 Bad Request` | Datos de entrada inválidos (falla validación) |
| `401 Unauthorized` | Token ausente, inválido o expirado |
| `403 Forbidden` | Rol insuficiente para la operación |
| `404 Not Found` | Recurso no encontrado |
| `409 Conflict` | Conflicto de negocio (duplicado, cupo lleno) |
| `429 Too Many Requests` | Rate limit excedido |
| `500 Internal Server Error` | Error inesperado del servidor |

---

## Esquema JWT

El payload del token JWT contiene:

```json
{
  "userId": "uuid-del-usuario",
  "email": "usuario@empresa.com",
  "role": "client",
  "iat": 1720000000,
  "exp": 1720007200
}
```
