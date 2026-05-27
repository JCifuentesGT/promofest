// PromoFest — Generador de presentación técnica
// Uso: node docs/gen_presentation.js
const pptxgen = require("pptxgenjs");

const OUT = "C:/Users/jccif/OneDrive/Documentos/GitHub/promofest/docs/PromoFest_Presentacion.pptx";

const C = {
  navy:   "1E2761",
  blue:   "3B82F6",
  green:  "10B981",
  red:    "EF4444",
  purple: "7C3AED",
  amber:  "D97706",
  white:  "FFFFFF",
  light:  "F8FAFC",
  dark:   "1F2937",
  gray:   "6B7280",
  mid:    "E2E8F0",
  ice:    "93C5FD",
  slate:  "64748B",
};

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";   // 10" × 5.625"
pres.author = "PromoFest";
pres.title  = "PromoFest — Presentación Técnica";

// ── helpers ───────────────────────────────────────────────────────────────────

function headerBar(slide, text, fontSize = 26) {
  slide.addShape(slide._slideObjects ? pres.shapes.RECTANGLE : pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.navy }, line: { color: C.navy }
  });
  slide.addText(text, {
    x: 0.45, y: 0, w: 9.1, h: 0.9,
    fontSize, fontFace: "Calibri", bold: true,
    color: C.white, valign: "middle", margin: 0
  });
}

function card(slide, x, y, w, h, opts = {}) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: opts.fill || C.white },
    shadow: { type: "outer", blur: 10, offset: 3, angle: 135, color: "000000", opacity: 0.09 },
    line: { color: opts.border || C.mid, width: 1 }
  });
  if (opts.accentColor) {
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.11, h,
      fill: { color: opts.accentColor }, line: { color: opts.accentColor }
    });
  }
}

function cardWithHeader(slide, x, y, w, h, headerText, headerColor) {
  card(slide, x, y, w, h);
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h: 0.48,
    fill: { color: headerColor }, line: { color: headerColor }
  });
  slide.addText(headerText, {
    x: x + 0.12, y, w: w - 0.12, h: 0.48,
    fontSize: 13, fontFace: "Calibri", bold: true,
    color: C.white, valign: "middle", margin: 0
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 1 — Portada
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Círculos decorativos
  s.addShape(pres.shapes.OVAL, {
    x: 7.2, y: -1.2, w: 4.2, h: 4.2,
    fill: { color: C.blue, transparency: 78 }, line: { color: C.navy }
  });
  s.addShape(pres.shapes.OVAL, {
    x: -0.6, y: 3.8, w: 2.8, h: 2.8,
    fill: { color: C.green, transparency: 82 }, line: { color: C.navy }
  });

  s.addText("PromoFest", {
    x: 0.65, y: 0.9, w: 8.5, h: 1.25,
    fontSize: 54, fontFace: "Calibri", bold: true,
    color: C.white, margin: 0
  });
  s.addText("Sistema de Confirmación de Asistencia", {
    x: 0.65, y: 2.1, w: 8.5, h: 0.55,
    fontSize: 20, fontFace: "Calibri", color: C.ice, margin: 0
  });

  s.addShape(pres.shapes.LINE, {
    x: 0.65, y: 2.82, w: 5.5, h: 0,
    line: { color: C.blue, width: 2 }
  });

  s.addText("Arquitectura full-stack para gestión de cupos bajo alta concurrencia", {
    x: 0.65, y: 3.0, w: 8.5, h: 0.45,
    fontSize: 13, fontFace: "Calibri", color: "CBD5E1", margin: 0
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 4.95, w: 10, h: 0.675,
    fill: { color: C.blue }, line: { color: C.blue }
  });
  s.addText("Feria de Promociones 2025  ·  React + Express + PostgreSQL  ·  Railway Cloud", {
    x: 0, y: 4.95, w: 10, h: 0.675,
    fontSize: 12, fontFace: "Calibri", bold: true,
    color: C.white, align: "center", valign: "middle"
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 2 — El Problema
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.light };
  headerBar(s, "El Reto — 50 cupos, cientos de solicitudes simultáneas");

  // Descripción izquierda
  s.addText([
    { text: "El formulario se distribuye por correo masivo.", options: { breakLine: true } },
    { text: "En los primeros minutos hay una ráfaga de envíos simultáneos.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 4 } },
    { text: "Sin control:", options: { bold: true, breakLine: true } },
    { text: "Dos usuarios leen confirmed_count = 49, ambos creen que hay lugar, ambos confirman → cupo superado.", options: {} },
  ], {
    x: 0.5, y: 1.05, w: 4.9, h: 2.0,
    fontSize: 13, fontFace: "Calibri", color: C.dark, valign: "top"
  });

  // Caja roja — problema
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.15, w: 4.9, h: 1.55,
    fill: { color: "FEF2F2" }, line: { color: C.red, width: 1.5 }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.15, w: 0.11, h: 1.55,
    fill: { color: C.red }, line: { color: C.red }
  });
  s.addText([
    { text: "Race condition sin control:", options: { bold: true, color: C.red, breakLine: true } },
    { text: "T1 lee cupo = 1 → cree que hay lugar", options: { breakLine: true } },
    { text: "T2 lee cupo = 1 → también cree que hay lugar", options: { breakLine: true } },
    { text: "Ambas insertan → cupo = 2 con límite de 1", options: {} },
  ], {
    x: 0.75, y: 3.22, w: 4.5, h: 1.4,
    fontSize: 12, fontFace: "Calibri", color: C.dark, valign: "top"
  });

  // Stat cards derecha
  const stats = [
    { num: "50",   label: "cupos disponibles",                    color: C.blue   },
    { num: "200+", label: "solicitudes en los primeros minutos",  color: C.amber  },
    { num: "0",    label: "confirmaciones duplicadas aceptadas",  color: C.green  },
  ];
  stats.forEach((st, i) => {
    const y = 1.05 + i * 1.5;
    card(s, 5.75, y, 3.9, 1.25, { accentColor: st.color });
    s.addText(st.num, {
      x: 6.0, y: y + 0.1, w: 3.5, h: 0.6,
      fontSize: 36, fontFace: "Calibri", bold: true, color: st.color, margin: 0
    });
    s.addText(st.label, {
      x: 6.0, y: y + 0.72, w: 3.5, h: 0.38,
      fontSize: 11.5, fontFace: "Calibri", color: C.gray, margin: 0
    });
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 3 — Arquitectura
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.light };
  headerBar(s, "Arquitectura del Sistema — 3 servicios en Railway Cloud");

  const svcs = [
    { x: 0.35, label: "Frontend", color: C.blue,
      items: ["React 18 + TypeScript", "Vite 5 + Tailwind CSS", "React Router v6", "React Hook Form + Zod", "Axios", "Nginx (SPA fallback)"] },
    { x: 3.55, label: "Backend",  color: C.green,
      items: ["Express + TypeScript", "Controller → Service → Repository", "JWT + bcryptjs", "Zod (validación)", "Rate limit 100 req/15 min", "Winston (logging)"] },
    { x: 6.75, label: "Database", color: C.purple,
      items: ["PostgreSQL 16", "6 tablas relacionales", "SELECT FOR UPDATE", "Patrón Outbox", "Seed idempotente", "Pool de conexiones (pg)"] },
  ];

  svcs.forEach(svc => {
    cardWithHeader(s, svc.x, 1.05, 3.0, 3.75, svc.label, svc.color);
    const bullets = svc.items.map((t, i) => ({
      text: t, options: { bullet: true, ...(i < svc.items.length - 1 ? { breakLine: true } : {}) }
    }));
    s.addText(bullets, {
      x: svc.x + 0.15, y: 1.65, w: 2.7, h: 3.05,
      fontSize: 12, fontFace: "Calibri", color: C.dark, valign: "top"
    });
  });

  // Flechas entre servicios
  s.addShape(pres.shapes.LINE, { x: 3.36, y: 2.95, w: 0.19, h: 0, line: { color: C.slate, width: 2 } });
  s.addShape(pres.shapes.LINE, { x: 6.56, y: 2.95, w: 0.19, h: 0, line: { color: C.slate, width: 2 } });
  s.addText("HTTPS", { x: 3.1, y: 2.68, w: 0.75, h: 0.28, fontSize: 9, color: C.slate, align: "center" });
  s.addText("pg pool", { x: 6.2, y: 2.68, w: 0.85, h: 0.28, fontSize: 9, color: C.slate, align: "center" });

  // Badge Railway
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 5.0, w: 9.3, h: 0.38,
    fill: { color: "EFF6FF" }, line: { color: C.blue, width: 1 }
  });
  s.addText("Desplegado en Railway  ·  Docker multi-stage  ·  CI/CD automático en cada push a main  ·  TLS gestionado", {
    x: 0.35, y: 5.0, w: 9.3, h: 0.38,
    fontSize: 11, fontFace: "Calibri", color: C.blue, align: "center", valign: "middle"
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 4 — Anti-Overbooking
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.light };
  headerBar(s, "Decisión Clave 1 — Control de Concurrencia (SELECT FOR UPDATE)");

  // Pasos del mecanismo (izquierda)
  s.addText("¿Cómo funciona?", {
    x: 0.5, y: 1.1, w: 4.8, h: 0.38,
    fontSize: 15, fontFace: "Calibri", bold: true, color: C.dark, margin: 0
  });

  const steps = [
    { n: "1", txt: "BEGIN TRANSACTION",                           color: C.blue   },
    { n: "2", txt: "SELECT event_config FOR UPDATE  ← bloquea la fila",  color: C.purple },
    { n: "3", txt: "IF cupo agotado → ROLLBACK + 409",           color: C.red    },
    { n: "4", txt: "INSERT attendee + UPDATE confirmed_count + 1", color: C.blue  },
    { n: "5", txt: "COMMIT  → libera el lock",                    color: C.green  },
  ];
  steps.forEach((st, i) => {
    const y = 1.6 + i * 0.67;
    s.addShape(pres.shapes.OVAL, {
      x: 0.5, y, w: 0.4, h: 0.4,
      fill: { color: st.color }, line: { color: st.color }
    });
    s.addText(st.n, {
      x: 0.5, y, w: 0.4, h: 0.4,
      fontSize: 12, bold: true, color: C.white,
      align: "center", valign: "middle", margin: 0
    });
    s.addText(st.txt, {
      x: 1.05, y: y + 0.04, w: 4.2, h: 0.34,
      fontSize: 12, fontFace: "Calibri", color: C.dark, valign: "middle", margin: 0
    });
  });

  // Por qué no Redis (top derecha)
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.55, y: 1.05, w: 4.1, h: 1.95,
    fill: { color: "EFF6FF" }, line: { color: C.blue, width: 1.5 }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.55, y: 1.05, w: 4.1, h: 0.4,
    fill: { color: C.blue }, line: { color: C.blue }
  });
  s.addText("¿Por qué no Redis INCR/DECR?", {
    x: 5.7, y: 1.05, w: 3.85, h: 0.4,
    fontSize: 12, fontFace: "Calibri", bold: true,
    color: C.white, valign: "middle", margin: 0
  });
  s.addText([
    { text: "Para 50–100 asistentes:", options: { bold: true, breakLine: true } },
    { text: "El lock de fila es suficiente. Redis introduce un segundo sistema de estado que debe sincronizarse con la DB.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 4 } },
    { text: "Con 1 000+ concurrentes:", options: { bold: true, color: C.amber, breakLine: true } },
    { text: "DECR atómico en Redis → rechazar sin abrir transacción Postgres.", options: {} },
  ], {
    x: 5.7, y: 1.5, w: 3.85, h: 1.45,
    fontSize: 11.5, fontFace: "Calibri", color: C.dark, valign: "top"
  });

  // Resultado garantizado (bottom derecha)
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.55, y: 3.15, w: 4.1, h: 1.65,
    fill: { color: "ECFDF5" }, line: { color: C.green, width: 1.5 }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.55, y: 3.15, w: 4.1, h: 0.4,
    fill: { color: C.green }, line: { color: C.green }
  });
  s.addText("Resultado garantizado", {
    x: 5.7, y: 3.15, w: 3.85, h: 0.4,
    fontSize: 12, fontFace: "Calibri", bold: true,
    color: C.white, valign: "middle", margin: 0
  });
  s.addText([
    { text: "Con 500 requests simultáneos al último cupo,", options: { breakLine: true } },
    { text: "exactamente 1 confirma.", options: { bold: true, breakLine: true } },
    { text: "Los demás reciben ", options: {} },
    { text: "409 Conflict", options: { bold: true, color: C.red } },
    { text: " de forma limpia.", options: {} },
  ], {
    x: 5.7, y: 3.62, w: 3.85, h: 1.1,
    fontSize: 12, fontFace: "Calibri", color: C.dark, valign: "top"
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 5 — Patrón Outbox
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.light };
  headerBar(s, "Decisión Clave 2 — Patrón Outbox (Notificaciones al equipo de ventas)");

  // Flujo horizontal
  const flowItems = [
    { label: "COMMIT\nexitoso",             color: C.green,  x: 0.35, w: 1.85 },
    { label: "INSERT\nnotification_log\n'pending'", color: C.purple, x: 2.55, w: 2.1 },
    { label: "simulateSend()\nWinston logger\n→ prod: SendGrid", color: C.blue, x: 5.0, w: 2.35 },
    { label: "status:\nsent / failed",      color: C.amber,  x: 7.7,  w: 1.95 },
  ];
  flowItems.forEach((f, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: f.x, y: 1.1, w: f.w, h: 0.88,
      fill: { color: f.color }, line: { color: f.color }
    });
    s.addText(f.label, {
      x: f.x, y: 1.1, w: f.w, h: 0.88,
      fontSize: 10, fontFace: "Calibri", bold: true,
      color: C.white, align: "center", valign: "middle"
    });
    if (i < flowItems.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: f.x + f.w, y: 1.54, w: 0.35, h: 0,
        line: { color: C.dark, width: 1.5 }
      });
    }
  });

  // Dos cards de insight
  const insights = [
    {
      x: 0.35, title: "Desacoplamiento total",
      color: C.green,
      body: "La notificación se persiste en la misma transacción que el asistente. El 'envío' ocurre fuera del COMMIT y no bloquea la respuesta al cliente.\n\nSi falla, la confirmación no se revierte. Queda status='failed' para reintento.",
    },
    {
      x: 5.1, title: "Listo para producción",
      color: C.purple,
      body: "Reemplazar simulateSend() con SendGrid, Twilio o un webhook de Slack es un cambio de una función sin tocar la lógica de negocio ni el patrón Outbox.\n\nIdempotency key en el notificador externo previene duplicados.",
    },
  ];
  insights.forEach(ins => {
    cardWithHeader(s, ins.x, 2.2, 4.5, 2.95, ins.title, ins.color);
    s.addText(ins.body, {
      x: ins.x + 0.2, y: 2.8, w: 4.1, h: 2.28,
      fontSize: 12, fontFace: "Calibri", color: C.dark, valign: "top"
    });
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 6 — Arquitectura de código (capas)
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.light };
  headerBar(s, "Arquitectura de Código — Controller → Service → Repository");

  const layers = [
    {
      x: 0.35, label: "Controller", color: C.blue,
      resp: "Recibe request, valida con Zod, llama al Service, devuelve response.",
      files: ["auth.controller.ts", "attendee.controller.ts"],
      detail: "No sabe nada de SQL ni de reglas de negocio."
    },
    {
      x: 3.55, label: "Service", color: C.green,
      resp: "Lógica de negocio pura: descuentos, orquestación de la confirmación.",
      files: ["attendee.service.ts", "auth.service.ts", "discount.service.ts", "notification.service.ts"],
      detail: "No sabe nada de Express ni de SQL. Testeable sin levantar nada."
    },
    {
      x: 6.75, label: "Repository", color: C.purple,
      resp: "Queries SQL. Recibe PoolClient cuando participa en una transacción externa.",
      files: ["auth.repository.ts", "attendee.repository.ts", "catalog.repository.ts"],
      detail: "No sabe nada de HTTP ni de lógica de negocio."
    },
  ];

  layers.forEach(l => {
    cardWithHeader(s, l.x, 1.05, 3.0, 4.15, l.label, l.color);
    s.addText(l.resp, {
      x: l.x + 0.15, y: 1.62, w: 2.7, h: 0.85,
      fontSize: 11.5, fontFace: "Calibri", color: C.dark, valign: "top"
    });
    const fileItems = l.files.map((f, i) => ({
      text: f, options: { bullet: true, ...(i < l.files.length - 1 ? { breakLine: true } : {}) }
    }));
    s.addText(fileItems, {
      x: l.x + 0.15, y: 2.55, w: 2.7, h: 1.4,
      fontSize: 11, fontFace: "Calibri", color: C.slate, valign: "top"
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: l.x + 0.15, y: 4.08, w: 2.7, h: 0.82,
      fill: { color: l.color, transparency: 88 }, line: { color: l.color, width: 1 }
    });
    s.addText(l.detail, {
      x: l.x + 0.25, y: 4.1, w: 2.5, h: 0.76,
      fontSize: 10.5, fontFace: "Calibri", italic: true, color: C.dark, valign: "middle"
    });
  });

  // Flechas entre capas
  s.addShape(pres.shapes.LINE, { x: 3.36, y: 3.12, w: 0.19, h: 0, line: { color: C.slate, width: 2 } });
  s.addShape(pres.shapes.LINE, { x: 6.56, y: 3.12, w: 0.19, h: 0, line: { color: C.slate, width: 2 } });
}

// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 7 — Límites conocidos
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.light };
  headerBar(s, "Lo que sé que falta — y cómo lo resolvería");

  const limits = [
    {
      issue: "Sin suite de tests",
      fix: "discount.service.ts es función pura — diseñada para ser testeable sin DB ni HTTP. La suite entraría en Jest desde el primer sprint.",
      color: C.amber
    },
    {
      issue: "JWT sin revocación",
      fix: "El token comprometido sigue válido hasta que expira (2h). Solución: allowlist en Redis con el jti del token. Logout invalida inmediatamente.",
      color: C.red
    },
    {
      issue: "Notificación simulada",
      fix: "simulateSend() es un placeholder. El patrón Outbox ya maneja estado y reintentos — solo hay que enchufar SendGrid, Twilio o SQS.",
      color: C.purple
    },
    {
      issue: "Lock bajo altísima carga",
      fix: "Con 1 000+ concurrentes, el lock de fila en PostgreSQL crea latencia de P99 inaceptable. Migrar a DECR atómico en Redis antes de abrir la transacción.",
      color: C.blue
    },
  ];

  limits.forEach((lim, i) => {
    const y = 1.1 + i * 1.12;
    card(s, 0.35, y, 9.3, 0.95, { accentColor: lim.color });
    s.addText(lim.issue, {
      x: 0.62, y: y + 0.08, w: 2.9, h: 0.35,
      fontSize: 13, fontFace: "Calibri", bold: true, color: lim.color, margin: 0
    });
    s.addText(lim.fix, {
      x: 0.62, y: y + 0.5, w: 8.9, h: 0.38,
      fontSize: 11.5, fontFace: "Calibri", color: C.gray, margin: 0
    });
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 5.06, w: 9.3, h: 0.35,
    fill: { color: "EFF6FF" }, line: { color: C.blue, width: 1 }
  });
  s.addText("Conocer los límites del sistema es parte del diseño — no una omisión.", {
    x: 0.35, y: 5.06, w: 9.3, h: 0.35,
    fontSize: 11.5, fontFace: "Calibri", italic: true, color: C.blue,
    align: "center", valign: "middle"
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 8 — Cierre
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addShape(pres.shapes.OVAL, {
    x: 7.5, y: -1.0, w: 4.0, h: 4.0,
    fill: { color: C.blue, transparency: 80 }, line: { color: C.navy }
  });
  s.addShape(pres.shapes.OVAL, {
    x: -0.7, y: 3.6, w: 2.8, h: 2.8,
    fill: { color: C.green, transparency: 84 }, line: { color: C.navy }
  });

  s.addText("\"Cuando el entorno falla,", {
    x: 0.7, y: 0.55, w: 9, h: 0.65,
    fontSize: 26, fontFace: "Calibri", italic: true, color: C.ice, margin: 0
  });
  s.addText("busco la solución que me permite seguir entregando.\"", {
    x: 0.7, y: 1.15, w: 9, h: 0.65,
    fontSize: 26, fontFace: "Calibri", italic: true, bold: true, color: C.white, margin: 0
  });

  s.addShape(pres.shapes.LINE, {
    x: 0.7, y: 2.0, w: 5.0, h: 0,
    line: { color: C.blue, width: 2 }
  });

  s.addText([
    { text: "Repositorio:", options: { bold: true, color: C.ice, breakLine: true } },
    { text: "github.com/JCifuentesGT/promofest", options: { color: C.white, breakLine: true } },
  ], {
    x: 0.7, y: 2.2, w: 8.5, h: 0.85,
    fontSize: 14, fontFace: "Calibri"
  });

  s.addText("React · Express · PostgreSQL · Railway · Docker · JWT · SELECT FOR UPDATE · Outbox Pattern", {
    x: 0.7, y: 3.25, w: 8.8, h: 0.4,
    fontSize: 11, fontFace: "Calibri", color: C.slate
  });

  // Conclusión final
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 3.85, w: 9.3, h: 1.0,
    fill: { color: C.blue }, line: { color: C.blue }
  });
  s.addText([
    { text: "Pienso en qué pasa cuando el sistema crece:", options: { bold: true, breakLine: true } },
    { text: "¿cuál es el cuello de botella? ¿qué cambiaría primero? ¿qué no cambiaría nunca?", options: {} },
  ], {
    x: 0.5, y: 3.85, w: 9.1, h: 1.0,
    fontSize: 14, fontFace: "Calibri", color: C.white,
    align: "center", valign: "middle"
  });

  // Footer
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.02, w: 10, h: 0.605,
    fill: { color: "0F172A" }, line: { color: "0F172A" }
  });
  s.addText("PromoFest — Feria de Promociones 2025", {
    x: 0, y: 5.02, w: 10, h: 0.605,
    fontSize: 11, fontFace: "Calibri", color: C.slate,
    align: "center", valign: "middle"
  });
}

// ── Guardar ───────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: OUT })
  .then(() => console.log(`[OK] Presentacion guardada en:\n     ${OUT}`))
  .catch(err => { console.error("Error:", err); process.exit(1); });
