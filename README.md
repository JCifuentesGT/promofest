# PromoFest — Sistema de Confirmación de Asistencia

> Plataforma web para gestionar la confirmación de cupos, selección de servicios y productos, y seguimiento de asistentes en la **Feria de Promociones 2025**.

---

## Tabla de contenidos

- [Descripción general](#descripción-general)
- [Arquitectura del sistema](#arquitectura-del-sistema)
- [Stack tecnológico](#stack-tecnológico)
- [Funcionalidades](#funcionalidades)
- [Inicio rápido — desarrollo local](#inicio-rápido--desarrollo-local)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Variables de entorno](#variables-de-entorno)
- [Reglas de negocio — Descuentos](#reglas-de-negocio--descuentos)
- [Documentación adicional](#documentación-adicional)

---

## Descripción general

PromoFest es una aplicación full-stack de dos servicios que permite a los asistentes de una feria corporativa:

1. **Registrarse e iniciar sesión** de forma segura con email y contraseña.
2. **Confirmar su cupo** eligiendo una sesión, servicios y productos del catálogo.
3. **Ver sus descuentos** calculados automáticamente según las reglas de negocio.

Al mismo tiempo, el **equipo de ventas** accede a un panel administrativo en tiempo real con todos los datos de los asistentes confirmados, sus selecciones y el estado de notificación.

---

## Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        Railway Cloud                         │
│                                                             │
│  ┌───────────────────┐       ┌─────────────────────────┐   │
│  │  Frontend Service  │       │    Backend Service       │   │
│  │                   │       │                         │   │
│  │  React + Vite     │──────▶│  Express + TypeScript   │   │
│  │  Nginx (SPA)      │       │  REST API               │   │
│  │  :443             │       │  :4000                  │   │
│  └───────────────────┘       └──────────┬──────────────┘   │
│                                         │                    │
│                              ┌──────────▼──────────┐        │
│                              │   PostgreSQL 16      │        │
│                              │   Database Service   │        │
│                              └─────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Diagrama de componentes

```mermaid
graph TB
    subgraph Browser["Navegador del usuario"]
        SPA["React SPA\n(Vite + TypeScript + Tailwind)"]
    end

    subgraph Railway["Railway Cloud"]
        subgraph FE_Service["Frontend Service (Docker)"]
            NGINX["Nginx\nSirve build estático\nSPA fallback → index.html"]
        end

        subgraph BE_Service["Backend Service (Docker)"]
            EXPRESS["Express API\n/api/auth\n/api/catalog\n/api/attendees"]
            RATE["Rate Limiter\n100 req / 15 min"]
            JWT_MW["JWT Middleware"]
            VALID["Zod Validator"]
        end

        subgraph DB_Service["Database (PostgreSQL 16)"]
            PG[("6 tablas\nusers · catalog_items\nevent_config · attendees\nattendee_items · notification_log")]
        end
    end

    SPA -->|"HTTPS"| NGINX
    NGINX --> SPA
    SPA -->|"HTTPS + Bearer token"| EXPRESS
    EXPRESS --> RATE --> JWT_MW --> VALID
    EXPRESS <-->|"pg pool"| PG
```

---

## Stack tecnológico

### Backend

| Tecnología | Versión | Uso |
|---|---|---|
| Node.js | 20 LTS | Runtime |
| TypeScript | 5.5 | Lenguaje tipado |
| Express | 4.19 | Framework HTTP |
| PostgreSQL (`pg`) | 8.12 | Base de datos relacional |
| `jsonwebtoken` | 9.0 | Autenticación stateless (JWT) |
| `bcryptjs` | 2.4 | Hash de contraseñas |
| Zod | 3.23 | Validación de esquemas |
| `express-rate-limit` | 7.3 | Protección contra abuso |
| Winston | 3.13 | Logging estructurado |

### Frontend

| Tecnología | Versión | Uso |
|---|---|---|
| React | 18.3 | UI Framework |
| TypeScript | 5.5 | Lenguaje tipado |
| Vite | 5.3 | Build tool y dev server |
| React Router v6 | 6.24 | Enrutamiento SPA |
| React Hook Form | 7.52 | Gestión de formularios |
| Zod + hookform/resolvers | 3.23 | Validación de formularios |
| Axios | 1.7 | Cliente HTTP |
| Tailwind CSS | 3.4 | Estilos utilitarios |
| date-fns | 3.6 | Formateo de fechas |
| clsx | 2.1 | Clases CSS condicionales |

### Infraestructura

| Servicio | Detalle |
|---|---|
| Railway | PaaS — aloja los 3 servicios (frontend, backend, DB) |
| Docker | Multi-stage build para frontend y backend |
| Nginx | Sirve el SPA; resuelve rutas client-side con `try_files` |
| GitHub | Control de versiones; trigger de deploys automáticos en Railway |

---

## Funcionalidades

### Clientes (usuarios registrados)

- Registro e inicio de sesión con email y contraseña
- Email pre-cargado desde la cuenta autenticada al completar el formulario
- Formulario en 2 pasos: datos personales + selección de catálogo
- Visualización de descuentos en tiempo real mientras seleccionan ítems
- Pantalla de éxito con resumen detallado al confirmar
- Bloqueo de re-confirmación: si ya confirmaron, ven sus datos existentes en lugar del formulario
- Indicador de cupos disponibles en tiempo real

### Equipo de ventas (rol admin)

- Login diferenciado con redirección automática al panel de ventas
- Dashboard con 4 KPIs: confirmados/capacidad, asistentes en filtro, servicios totales, productos totales
- Tabla completa de asistentes con: nombre, email, sesión, servicios, productos, descuentos, fecha y estado de notificación
- Filtro por nombre o email
- Filtro por fecha de sesión

### Sistema

- Prevención de overbooking mediante bloqueo a nivel de base de datos (`SELECT ... FOR UPDATE`)
- Patrón Outbox para notificaciones asíncronas al equipo de ventas
- Rate limiting global: 100 solicitudes por IP cada 15 minutos
- JWT con expiración configurable
- Rutas protegidas por rol (`client` / `admin`)
- Seed automático del catálogo y usuario admin en cada arranque (idempotente)

---

## Inicio rápido — desarrollo local

### Prerrequisitos

- Node.js 20+
- PostgreSQL 14+ corriendo localmente
- npm 9+

### 1. Clonar el repositorio

```bash
git clone https://github.com/JCifuentesGT/promofest.git
cd promofest
```

### 2. Configurar el backend

```bash
cd backend
npm install
```

Crear el archivo `backend/.env`:

```env
PORT=4000
DATABASE_URL=postgresql://usuario:password@localhost:5432/promofest
JWT_SECRET=super-secret-dev-key-minimo-32-caracteres
JWT_EXPIRES_IN=2h
FRONTEND_URL=http://localhost:5173
EVENT_CAPACITY=50
ADMIN_EMAIL=admin@promofest.com
ADMIN_PASSWORD=Admin1234!
```

```bash
npm run dev
```

El backend ejecuta las migraciones y seeds automáticamente al arrancar.

### 3. Configurar el frontend

```bash
cd frontend
npm install
```

Crear el archivo `frontend/.env`:

```env
VITE_API_URL=http://localhost:4000
```

```bash
npm run dev
```

### 4. URLs locales

| URL | Descripción |
|---|---|
| `http://localhost:5173` | Aplicación de clientes |
| `http://localhost:5173/admin` | Panel de ventas |
| `http://localhost:4000/health` | Health check del API |

---

## Estructura del proyecto

```
promofest/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   │   ├── database.ts           # Pool de conexiones PostgreSQL
│   │   │   └── migrations.ts         # DDL + seeds (catálogo y admin)
│   │   ├── controllers/
│   │   │   ├── auth.controller.ts    # login / register / me
│   │   │   └── attendee.controller.ts # confirm / me / listAll
│   │   ├── middleware/
│   │   │   ├── auth.ts               # authenticate + requireAdmin
│   │   │   └── validate.ts           # Validador Zod genérico
│   │   ├── repositories/
│   │   │   ├── auth.repository.ts    # CRUD de usuarios
│   │   │   ├── attendee.repository.ts # Asistentes + event_config
│   │   │   └── catalog.repository.ts  # Lectura del catálogo
│   │   ├── routes/
│   │   │   ├── auth.routes.ts
│   │   │   ├── attendee.routes.ts
│   │   │   └── catalog.routes.ts
│   │   ├── services/
│   │   │   ├── attendee.service.ts   # Orquestador (transacción DB)
│   │   │   ├── auth.service.ts       # Lógica de auth + JWT
│   │   │   ├── discount.service.ts   # Cálculo puro de descuentos
│   │   │   └── notification.service.ts # Patrón Outbox
│   │   ├── types/index.ts            # Interfaces TypeScript
│   │   ├── utils/logger.ts           # Winston logger
│   │   └── index.ts                  # Entry point + bootstrap
│   ├── Dockerfile
│   ├── railway.json
│   └── package.json
│
├── frontend/
│   ├── src/
│   │   ├── components/ui/            # Componentes reutilizables
│   │   ├── context/
│   │   │   └── AuthContext.tsx       # Estado global de autenticación
│   │   ├── hooks/
│   │   │   └── useDiscounts.ts       # Descuentos en tiempo real
│   │   ├── pages/
│   │   │   ├── AuthPage.tsx          # Login / Register
│   │   │   ├── ConfirmPage.tsx       # Orquestador del flujo
│   │   │   ├── StepOne.tsx           # Paso 1: datos personales
│   │   │   ├── StepTwo.tsx           # Paso 2: selección de catálogo
│   │   │   ├── ConfirmationSuccess.tsx # Pantalla de éxito
│   │   │   ├── AlreadyConfirmed.tsx  # "Ya confirmaste"
│   │   │   └── AdminPage.tsx         # Panel de ventas
│   │   ├── services/index.ts         # Axios + llamadas al API
│   │   ├── types/index.ts            # Interfaces TypeScript
│   │   └── App.tsx                   # Router + guards de ruta
│   ├── nginx.conf                    # Config Nginx con SPA fallback
│   ├── Dockerfile                    # Multi-stage: build + Nginx
│   ├── railway.json
│   └── package.json
│
├── docs/
│   ├── API.md           # Referencia completa de endpoints
│   ├── DATABASE.md      # Esquema ER y descripción de tablas
│   ├── FLOWS.md         # Diagramas de flujo
│   └── DEPLOYMENT.md    # Guía de despliegue en Railway
│
├── DECISIONS.md         # Decisiones de arquitectura
└── README.md
```

---

## Variables de entorno

### Backend

| Variable | Requerida | Default | Descripción |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | URL de conexión PostgreSQL |
| `JWT_SECRET` | ✅ | `changeme` | Clave para firmar tokens JWT |
| `PORT` | auto | `4000` | Puerto del servidor (Railway lo inyecta) |
| `JWT_EXPIRES_IN` | — | `2h` | Tiempo de vida del token |
| `FRONTEND_URL` | — | `*` | Origen permitido por CORS |
| `EVENT_CAPACITY` | — | `50` | Cupo máximo del evento |
| `ADMIN_EMAIL` | — | — | Email del usuario administrador |
| `ADMIN_PASSWORD` | — | — | Contraseña del usuario administrador |

### Frontend

| Variable | Requerida | Descripción |
|---|---|---|
| `VITE_API_URL` | ✅ | URL base del backend (se bake en build time) |

> **Nota importante:** `VITE_API_URL` es una variable de **tiempo de compilación**. Vite la reemplaza estáticamente en el bundle JavaScript durante `npm run build`. Debe configurarse en las variables del servicio frontend en Railway **antes** del deploy.

---

## Reglas de negocio — Descuentos

Los descuentos se calculan en el backend al confirmar y se muestran en tiempo real en el frontend.

### Servicios

| Condición | Descuento |
|---|---|
| 2 o más servicios seleccionados | **3 %** |
| 2 o más servicios **Y** precio total > Q.1,500 | **5 %** |

### Productos

| Condición | Descuento |
|---|---|
| 3 o 4 productos seleccionados | **3 %** |
| 5 o más productos seleccionados | **5 %** |

Los descuentos de servicios y productos son independientes entre sí.

---

## Documentación adicional

| Documento | Descripción |
|---|---|
| [docs/API.md](docs/API.md) | Referencia completa de endpoints REST |
| [docs/DATABASE.md](docs/DATABASE.md) | Diagrama ER y descripción de tablas |
| [docs/FLOWS.md](docs/FLOWS.md) | Diagramas de flujo: confirmación, auth, notificaciones |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Guía paso a paso para desplegar en Railway |
| [DECISIONS.md](DECISIONS.md) | Decisiones de arquitectura y razonamiento técnico |

---

*PromoFest — Feria de Promociones 2025*
