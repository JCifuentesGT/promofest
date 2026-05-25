# PromoFest — Diagramas de Flujo

---

## 1. Flujo de autenticación

### 1.1 Registro de usuario

```mermaid
flowchart TD
    A([Usuario abre la app]) --> B[Muestra formulario Login/Register]
    B --> C{¿Tiene cuenta?}
    C -- Sí --> D[Ingresa email + contraseña]
    C -- No --> E[Completa registro]
    E --> F[POST /api/auth/register]
    D --> G[POST /api/auth/login]

    F --> H{¿Email ya registrado?}
    H -- Sí --> I[Error 409 — Email en uso]
    I --> E
    H -- No --> J[Crea usuario role=client\nHash bcrypt del password]

    G --> K{¿Credenciales válidas?}
    K -- No --> L[Error 401 — Credenciales incorrectas]
    L --> D
    K -- Sí --> M[Firma JWT con userId + email + role]

    J --> M
    M --> N[Guarda token + user en localStorage]
    N --> O{¿role === admin?}
    O -- Sí --> P[Redirige a /admin]
    O -- No --> Q[Redirige a /confirm]
```

---

### 1.2 Rutas protegidas (guardas de ruta)

```mermaid
flowchart LR
    User([Usuario]) --> URL[Accede a URL]

    URL --> R1{"/login"}
    R1 --> G1{PublicRoute\n¿autenticado?}
    G1 -- No --> ShowLogin[Muestra AuthPage]
    G1 -- Sí --> RoleCheck1{role === admin?}
    RoleCheck1 -- Sí --> GoAdmin[→ /admin]
    RoleCheck1 -- No --> GoConfirm[→ /confirm]

    URL --> R2{"/confirm"}
    R2 --> G2{ProtectedRoute\n¿autenticado?}
    G2 -- No --> GoLogin[→ /login]
    G2 -- Sí --> ShowConfirm[Muestra ConfirmPage]

    URL --> R3{"/admin"}
    R3 --> G3{AdminRoute\n¿autenticado?}
    G3 -- No --> GoLogin2[→ /login]
    G3 -- Sí --> G4{role === admin?}
    G4 -- No --> GoConfirm2[→ /confirm]
    G4 -- Sí --> ShowAdmin[Muestra AdminPage]

    URL --> R4{"Cualquier otra\nruta (*)"}
    R4 --> G5{HomeRedirect\n¿autenticado?}
    G5 -- No --> GoLogin3[→ /login]
    G5 -- Sí --> RoleCheck2{role === admin?}
    RoleCheck2 -- Sí --> GoAdmin2[→ /admin]
    RoleCheck2 -- No --> GoConfirm3[→ /confirm]
```

---

## 2. Flujo de confirmación de asistencia

### 2.1 Diagrama general del usuario

```mermaid
flowchart TD
    Start([Usuario en /confirm]) --> Loading[Carga en paralelo:\nCatálogo + Estado evento\n+ Confirmación existente]

    Loading --> Check{¿Ya confirmó\nanteriormente?}
    Check -- Sí --> AlreadyDone[Muestra pantalla\nAlreadyConfirmed\ncon sus datos]
    AlreadyDone --> Logout([Cerrar sesión])

    Check -- No --> EventFull{¿Evento lleno?}
    EventFull -- Sí --> FullBanner[Muestra banner\nEvento completo]

    EventFull -- No --> Step1[PASO 1\nNombre · Apellido\nEmail bloqueado · Sesión]
    Step1 --> Validate1{¿Datos válidos?}
    Validate1 -- No --> Step1
    Validate1 -- Sí --> Step2[PASO 2\nSelección de catálogo\nDescuentos en tiempo real]

    Step2 --> Validate2{¿Al menos 1 ítem?}
    Validate2 -- No --> Step2
    Validate2 -- Sí --> Submit[POST /api/attendees/confirm]

    Submit --> APIResult{¿Resultado?}
    APIResult -- Error 409 cupo lleno --> FullError[Muestra error\nEvento completo]
    APIResult -- Error 409 duplicado --> DupError[Muestra error\nEmail ya registrado]
    APIResult -- Error genérico --> GenError[Muestra error]
    APIResult -- 201 OK --> Success[Muestra ConfirmationSuccess\ncon resumen y descuentos]

    Success --> NewOrLogout{Usuario elige}
    NewOrLogout -- Nueva confirmación --> Step1
    NewOrLogout -- Cerrar sesión --> Logout
```

---

### 2.2 Secuencia de confirmación (backend)

```mermaid
sequenceDiagram
    actor User as Usuario
    participant FE as Frontend (React)
    participant BE as Express API
    participant DB as PostgreSQL

    User->>FE: Completa Paso 1 y Paso 2
    User->>FE: Clic "Confirmar asistencia"
    FE->>BE: POST /api/attendees/confirm\n{first_name, last_name, email, attend_at, item_ids[]}

    BE->>BE: Middleware: valida JWT
    BE->>BE: Middleware: valida Zod schema

    BE->>DB: SELECT catalog_items WHERE id IN (item_ids)
    DB-->>BE: items[]

    alt Ítem(s) no encontrados
        BE-->>FE: 400 — Ítems inválidos
    end

    BE->>DB: SELECT attendees WHERE email = $1
    DB-->>BE: existing?

    alt Email ya confirmado
        BE-->>FE: 409 — Ya existe confirmación
    end

    BE->>BE: calculateDiscounts(items)\n[función pura, sin I/O]

    BE->>DB: BEGIN TRANSACTION
    BE->>DB: SELECT event_config WHERE id=1 FOR UPDATE
    DB-->>BE: {capacity, confirmed_count}

    alt Cupo agotado
        BE->>DB: ROLLBACK
        BE-->>FE: 409 — Evento lleno
    end

    BE->>DB: INSERT INTO attendees (...)
    DB-->>BE: attendee

    BE->>DB: INSERT INTO attendee_items (...)
    BE->>DB: UPDATE event_config SET confirmed_count = confirmed_count + 1
    BE->>DB: COMMIT

    Note over BE,DB: Transacción cerrada — cupo seguro

    BE->>DB: SELECT attendee + items (para respuesta)
    DB-->>BE: fullAttendee

    BE->>BE: notifySalesTeam() [async, no bloquea]
    BE-->>FE: 201 — {attendee, discounts, spots_remaining}
    FE-->>User: Pantalla de éxito con resumen

    Note over BE,DB: Notificación se procesa en paralelo
    BE->>DB: INSERT notification_log (status='pending')
    BE->>BE: simulateSend() → logger.info
    BE->>DB: UPDATE notification_log (status='sent')
    BE->>DB: UPDATE attendees SET notified_at=now()
```

---

## 3. Mecanismo anti-overbooking

```mermaid
sequenceDiagram
    participant T1 as Transacción 1\n(Usuario A)
    participant T2 as Transacción 2\n(Usuario B)
    participant DB as PostgreSQL\nevent_config (1 cupo)

    Note over T1,T2: Llegan simultáneamente — 1 cupo disponible

    T1->>DB: BEGIN
    T2->>DB: BEGIN

    T1->>DB: SELECT ... FOR UPDATE
    Note over DB: T1 adquiere el lock

    T2->>DB: SELECT ... FOR UPDATE
    Note over DB: T2 ESPERA — bloqueada por T1

    DB-->>T1: spots_remaining = 1 ✅

    T1->>DB: INSERT attendee
    T1->>DB: UPDATE confirmed_count + 1
    T1->>DB: COMMIT
    Note over DB: T1 libera el lock

    DB-->>T2: spots_remaining = 0 ❌

    T2->>DB: ROLLBACK
    T2-->>T2: Error 409 — Evento lleno
```

---

## 4. Patrón Outbox — Notificaciones

```mermaid
flowchart TD
    Confirm[Confirmación COMMIT exitoso] --> Notify

    subgraph Notify["notifySalesTeam() — async, fuera de la transacción"]
        N1[INSERT notification_log\nstatus='pending'] --> N2[simulateSend\nactual: logger.info\nproducción: SendGrid / SQS / Twilio]
        N2 --> N3{¿Envío exitoso?}
        N3 -- Sí --> N4[UPDATE notification_log\nstatus='sent', sent_at=now\nUPDATE attendees notified_at=now]
        N3 -- No --> N5[UPDATE notification_log\nstatus='failed', last_error=msg]
    end

    N5 --> Retry[Registro disponible\npara retry manual\no job programado]
    N4 --> Dashboard[Admin ve ✓\nen columna Notif.]

    Note1[/"La confirmación del usuario\nNO se revierte si la\nnotificación falla"/]
```

---

## 5. Flujo del panel de ventas (Admin)

```mermaid
flowchart TD
    AdminLogin([Admin hace login]) --> Redirect[Redirige a /admin\nAdminRoute verifica role=admin]

    Redirect --> LoadData[GET /api/attendees\nCarga todos los asistentes\n+ estadísticas del evento]

    LoadData --> Dashboard[Muestra Dashboard]

    Dashboard --> KPIs[KPIs:\n• Confirmados / Capacidad\n• En filtro actual\n• Total servicios\n• Total productos]

    Dashboard --> Filters{Aplica filtros}
    Filters --> SearchFilter[Búsqueda por\nnombre o email]
    Filters --> DateFilter[Filtro por\nfecha de sesión]

    SearchFilter --> Table[Tabla actualizada\nen tiempo real\n sin nueva llamada al API]
    DateFilter --> Table

    Table --> Cols[Columnas:\nAsistente · Email · Sesión\nServicios · Productos\nDesc. Serv. · Desc. Prod.\nConfirmado · Notif.]
```
