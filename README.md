# PromoFest 🎪

Plataforma de confirmación de asistencia para la Feria de Promociones Anual.

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + TypeScript + Vite + TailwindCSS |
| Backend | Node.js + TypeScript + Express |
| Base de datos | PostgreSQL 16 |
| Contenedores | Docker + Docker Compose |

## Levantar el proyecto localmente

### Requisitos
- Docker Desktop (o Docker + Docker Compose)
- Node.js 20+ (solo para desarrollo sin Docker)

### Con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone <repo-url> && cd promofest

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Levantar todos los servicios
docker compose up --build
```

La plataforma estará disponible en:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:4000
- **Health check:** http://localhost:4000/health

### Sin Docker (desarrollo)

```bash
# Backend
cd backend && npm install && npm run dev

# Frontend (nueva terminal)
cd frontend && npm install && npm run dev
```

> Requiere una instancia de PostgreSQL corriendo localmente con las variables del `.env`.

## Estructura del repositorio

```
promofest/
├── backend/
│   ├── src/
│   │   ├── config/        # DB, migraciones
│   │   ├── controllers/   # Lógica de request/response
│   │   ├── services/      # Lógica de negocio
│   │   ├── repositories/  # Acceso a datos
│   │   ├── middleware/    # Auth, validación, rate-limit
│   │   ├── routes/        # Definición de rutas
│   │   ├── types/         # Tipos TypeScript
│   │   └── utils/         # Logger, helpers
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes reutilizables
│   │   ├── pages/         # Vistas principales
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # Llamadas a la API
│   │   ├── context/       # Auth context
│   │   └── types/         # Tipos compartidos
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── DECISIONS.md
└── README.md
```

## Reglas de descuento

| Tipo | Condición | Descuento |
|------|-----------|-----------|
| Servicios | 2 o más seleccionados | 3% |
| Servicios | 2 o más **y** precio total > Q.1,500 | 5% |
| Productos | 3 o más seleccionados | 3% |
| Productos | 5 o más seleccionados | 5% |

## Capacidad del evento

El evento tiene un cupo máximo de **50 asistentes**. Configurable via `EVENT_CAPACITY` en `.env`.

## Documentación técnica

Ver [DECISIONS.md](./DECISIONS.md) para decisiones de arquitectura y razonamiento técnico.
