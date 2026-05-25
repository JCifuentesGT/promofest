# PromoFest — Guía de Despliegue en Railway

Esta guía cubre el despliegue completo de los tres servicios (frontend, backend, base de datos) en [Railway](https://railway.app).

---

## Arquitectura de despliegue

```
GitHub (main branch)
    │
    │  push → trigger automático
    ▼
Railway Project "promofest"
    ├── Frontend Service   (Docker multi-stage → Nginx)
    ├── Backend Service    (Docker → Node.js)
    └── PostgreSQL Service (managed by Railway)
```

Cada push a la rama `main` en GitHub dispara automáticamente el redeploy de ambos servicios.

---

## Prerrequisitos

- Cuenta en [Railway](https://railway.app)
- Repositorio en GitHub con el código de PromoFest
- Railway CLI (opcional, para comandos desde terminal)

---

## Paso 1 — Crear el proyecto en Railway

1. Ingresar a [railway.app](https://railway.app) → **New Project**
2. Seleccionar **"Deploy from GitHub repo"**
3. Conectar la cuenta de GitHub si no está conectada
4. Seleccionar el repositorio `promofest`

> Railway detectará automáticamente que hay múltiples servicios. Si no, se añaden manualmente en los pasos siguientes.

---

## Paso 2 — Añadir PostgreSQL

1. Dentro del proyecto → **Add Service** → **Database** → **PostgreSQL**
2. Railway aprovisiona la instancia automáticamente
3. Copiar la variable `DATABASE_URL` desde la pestaña **Variables** del servicio PostgreSQL (se usa en el backend)

---

## Paso 3 — Configurar el Backend

### 3.1 Crear el servicio

1. **Add Service** → **GitHub Repo** → seleccionar `promofest`
2. En **Settings** → **Root Directory** → escribir `backend`
3. Railway usará el `Dockerfile` en `backend/Dockerfile`

### 3.2 Variables de entorno

Ir a la pestaña **Variables** del servicio backend y agregar:

| Variable 			| Valor 								| Notas |
|---				|---									|---|
| `DATABASE_URL` 	| `${{PostgreSQL.DATABASE_URL}}`		| Referencia al servicio PostgreSQL |
| `JWT_SECRET` 		| cadena aleatoria segura ≥ 32 chars 	| Ej: usar `openssl rand -hex 32` |
| `JWT_EXPIRES_IN`	| `2h` 									| Opcional — default `2h` |
| `FRONTEND_URL` 	| URL del servicio frontend 			| Se configura después de crear el frontend |
| `EVENT_CAPACITY` 	| `50` 									| Opcional — default 50 |
| `ADMIN_EMAIL` 	| `ventas@empresa.com` 					| Email del usuario administrador |
| `ADMIN_PASSWORD` 	| contraseña segura 					| Mínimo 8 chars, incluir mayúsculas y símbolos |

> **Seguridad:** Nunca usar contraseñas débiles como `123456` en producción. El admin tiene acceso a los datos de todos los asistentes.

### 3.3 Verificar el deploy

Una vez desplegado, el endpoint de health check debe responder:

```bash
curl https://<backend-url>.railway.app/health
# {"status":"ok","timestamp":"2025-..."}
```

Revisar los logs del servicio para confirmar:
```
✅ Migrations complete
✅ Catalog seeded
✅ Admin user ready: ventas@empresa.com (role: admin)
🚀 Backend running on http://localhost:4000
```

---

## Paso 4 — Configurar el Frontend

### 4.1 Crear el servicio

1. **Add Service** → **GitHub Repo** → seleccionar `promofest`
2. En **Settings** → **Root Directory** → escribir `frontend`
3. Railway usará el `Dockerfile` en `frontend/Dockerfile`

### 4.2 Variables de entorno (Build Args)

> **Importante:** `VITE_API_URL` es una variable de **tiempo de compilación**. Vite la reemplaza estáticamente en el JavaScript bundle durante `docker build`. Debe estar disponible como `--build-arg`.

Ir a la pestaña **Variables** del servicio frontend:

| Variable 		| Valor 							  |
|---			|---								  |
| `VITE_API_URL`| `https://<backend-url>.railway.app` |

El `Dockerfile` del frontend declara `ARG VITE_API_URL` y `ENV VITE_API_URL=$VITE_API_URL` antes del `npm run build`, lo que permite a Railway pasarla durante el build.

### 4.3 Actualizar CORS en el backend

Con la URL del frontend disponible, actualizar en el backend:

| Variable 			| Valor 								|
|---				|---									|
| `FRONTEND_URL` 	| `https://<frontend-url>.railway.app` 	|

---

## Paso 5 — Verificar el despliegue completo

### Checklist

- [ ] Backend responde en `GET /health` con `{"status":"ok"}`
- [ ] Frontend carga en la URL del servicio
- [ ] Login funciona (probar con usuario normal)
- [ ] Login de admin redirige a `/admin`
- [ ] Formulario de confirmación muestra el catálogo
- [ ] Confirmación de asistencia retorna descuentos correctos
- [ ] Panel de admin muestra el asistente recién confirmado

---

## Archivos Docker

### `backend/Dockerfile`

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 4000
CMD ["node", "dist/index.js"]
```

### `frontend/Dockerfile`

```dockerfile
# Stage 1: build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Variables de build-time (Railway pasa VITE_API_URL como --build-arg)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: serve con Nginx
FROM nginx:alpine AS runner
ENV PORT=80
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template
EXPOSE 80
CMD ["/docker-entrypoint.sh", "nginx", "-g", "daemon off;"]
```

### `frontend/nginx.conf`

```nginx
server {
    listen ${PORT};
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # SPA fallback — todas las rutas sirven index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache agresivo para assets con hash en el nombre
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## Troubleshooting

### El frontend llama a `localhost:4000` en producción

**Causa:** `VITE_API_URL` no estaba disponible durante el `docker build`.  
**Solución:** Verificar que la variable esté configurada en Railway **antes** del deploy. Si ya existe el deploy, forzar un nuevo build haciendo un push o trigger manual.

**Verificación:** Descargar el JS bundle del frontend y buscar la URL:
```bash
curl https://<frontend-url>/assets/index-*.js | grep -o 'baseURL:"[^"]*"'
```

---

### El usuario admin inicia sesión pero ve `/confirm`

**Causa:** El usuario existía con `role = 'client'` en la base de datos antes de configurar las variables admin, o hay un token antiguo en localStorage.  
**Solución:**
1. Verificar en los logs del backend que aparezca `✅ Admin user ready: ... (role: admin)`
2. Cerrar sesión completamente (localStorage limpiado) y volver a iniciar sesión

---

### Error CORS al llamar al API desde el frontend

**Causa:** `FRONTEND_URL` en el backend no coincide exactamente con la URL del frontend.  
**Solución:** Asegurarse de que `FRONTEND_URL` tiene el formato exacto con `https://` y sin barra final:
```
FRONTEND_URL=https://promofest-frontend.up.railway.app
```

---

### El backend falla al arrancar con error de DB

**Causa:** `DATABASE_URL` inválida o el servicio PostgreSQL no está listo.  
**Solución:**
1. Verificar que `DATABASE_URL` referencia correctamente al servicio PostgreSQL: `${{PostgreSQL.DATABASE_URL}}`
2. En Railway, el servicio PostgreSQL puede tardar unos segundos en estar disponible; el backend reintentará la conexión

---

## Actualizaciones y redeploys

Para actualizar cualquier servicio:

```bash
git add .
git commit -m "descripción del cambio"
git push origin main
```

Railway detecta el push y redespliega automáticamente solo los servicios cuyo directorio raíz (`backend/` o `frontend/`) tenga cambios.

> **Nota sobre el seed del catálogo:** El seed solo inserta el catálogo si la tabla `catalog_items` está vacía. En redeploys normales, los datos existentes no se modifican. El seed del admin sí se ejecuta en cada arranque (upsert idempotente).

---

## Variables de entorno — resumen completo

### Backend Service

| Variable 			| Requerida | Descripción |
|---				|---		|---|
| `DATABASE_URL`	| ✅ 		| URL de conexión PostgreSQL |
| `JWT_SECRET` 		| ✅ 		| Clave secreta para JWT (≥ 32 chars) |
| `PORT` 			| auto 		| Inyectado por Railway |
| `JWT_EXPIRES_IN` 	| — 		| Default: `2h` |
| `FRONTEND_URL` 	| — 		| URL del frontend para CORS |
| `EVENT_CAPACITY` 	| — 		| Default: `50` |
| `ADMIN_EMAIL` 	| — 		| Email del administrador |
| `ADMIN_PASSWORD` 	| — 		| Contraseña del administrador |

### Frontend Service

| Variable 		| Requerida | Descripción |
|---			|---		|---								|
| `VITE_API_URL`| ✅ 		| URL base del backend (build-time) |
| `PORT` 		| auto 		| Inyectado por Railway en runtime |
