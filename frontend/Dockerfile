# ── Stage 1: build ──────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Declare build-time arg so Railway can pass VITE_API_URL during docker build
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ── Stage 2: serve with Nginx ────────────────────────────
FROM nginx:alpine AS runner

# Railway injects PORT at runtime; default to 80 for local dev
ENV PORT=80

COPY --from=builder /app/dist /usr/share/nginx/html
# Use the nginx:alpine template entrypoint — it runs envsubst on *.template files
# and writes the result to /etc/nginx/conf.d/, substituting only defined env vars.
# nginx variables like $uri are NOT substituted because they are not env variables.
COPY nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80

CMD ["/docker-entrypoint.sh", "nginx", "-g", "daemon off;"]
