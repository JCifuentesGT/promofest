#!/usr/bin/env python3
"""
PromoFest — Generador de diagramas de flujo (PDF)
================================================
Uso:
    pip install matplotlib
    python docs/generate_diagrams.py

Salida: docs/PromoFest_Diagramas.pdf
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "PromoFest_Diagramas.pdf")

# ── Paleta de colores ─────────────────────────────────────────────────────────
BLUE   = "#3B82F6"   # proceso
AMBER  = "#D97706"   # decisión
GREEN  = "#10B981"   # inicio / fin / éxito
RED    = "#EF4444"   # error
PURPLE = "#7C3AED"   # base de datos / async
GRAY   = "#6B7280"   # notas / async
ORANGE = "#F97316"   # admin
DARK   = "#1F2937"
BG     = "#F8FAFC"


# ── Helpers ───────────────────────────────────────────────────────────────────

def new_fig(title: str, subtitle: str = "", size=(11, 8.5)):
    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # Header bar
    bar = FancyBboxPatch((0, 11.2), 16, 0.8, boxstyle="square",
                         facecolor=BLUE, edgecolor="none", zorder=5)
    ax.add_patch(bar)
    ax.text(0.3, 11.6, "PromoFest", fontsize=9, color="white",
            va="center", alpha=0.8, zorder=6)
    ax.text(8, 11.6, title, fontsize=13, fontweight="bold",
            color="white", ha="center", va="center", zorder=6)
    if subtitle:
        ax.text(15.7, 11.6, subtitle, fontsize=7.5, color="white",
                va="center", ha="right", alpha=0.8, zorder=6)

    # Footer
    ax.text(8, 0.15, "Feria de Promociones 2025 — Documentación técnica",
            fontsize=7, color=GRAY, ha="center")
    return fig, ax


def box(ax, x, y, w, h, text, color=BLUE, fc="white", fontsize=8.5):
    """Rectángulo redondeado con texto centrado."""
    pad_x, pad_y = w / 2, h / 2
    rect = FancyBboxPatch((x - pad_x, y - pad_y), w, h,
                           boxstyle="round,pad=0.08",
                           facecolor=color, edgecolor="white",
                           linewidth=2, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=fc if fc != "white" else "white",
            fontweight="bold", zorder=4, multialignment="center",
            linespacing=1.4)


def diamond(ax, x, y, w, h, text, color=AMBER, fontsize=8):
    """Rombo de decisión."""
    pts = np.array([[x, y + h/2],
                    [x + w/2, y],
                    [x, y - h/2],
                    [x - w/2, y]])
    poly = plt.Polygon(pts, facecolor=color, edgecolor="white",
                       linewidth=2, zorder=3)
    ax.add_patch(poly)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4, multialignment="center")


def terminal(ax, x, y, text, color=GREEN):
    """Cápsula redondeada para inicio/fin."""
    rect = FancyBboxPatch((x - 1.3, y - 0.35), 2.6, 0.7,
                           boxstyle="round,pad=0.18",
                           facecolor=color, edgecolor="white",
                           linewidth=2, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y, text, ha="center", va="center", fontsize=9,
            color="white", fontweight="bold", zorder=4)


def arr(ax, x1, y1, x2, y2, label="", color=DARK, lw=1.6, rad=0.0):
    """Flecha entre dos puntos."""
    conn = f"arc3,rad={rad}" if rad else "arc3,rad=0"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color,
                                lw=lw, connectionstyle=conn))
    if label:
        mx = (x1 + x2) / 2 + (0.15 if x2 >= x1 else -0.15)
        my = (y1 + y2) / 2
        ax.text(mx, my, label, fontsize=7, color=color,
                style="italic", ha="center")


def note(ax, x, y, text, color=GRAY):
    ax.text(x, y, text, fontsize=7.5, color=color,
            style="italic", ha="center", va="center")


def legend_item(ax, x, y, color, label):
    rect = FancyBboxPatch((x, y - 0.13), 0.35, 0.26,
                           boxstyle="round,pad=0.04",
                           facecolor=color, edgecolor="none", zorder=3)
    ax.add_patch(rect)
    ax.text(x + 0.45, y, label, fontsize=7.5, color=DARK, va="center")


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — Portada
# ═══════════════════════════════════════════════════════════════════════════════

def page_cover(pdf):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(DARK)
    ax.set_facecolor(DARK)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7)
    ax.axis("off")

    # Fondo decorativo
    for i, (cx, cy, r, alpha) in enumerate([
        (1, 6, 2, 0.06), (9, 1, 2.5, 0.05), (5, 3.5, 4, 0.04)
    ]):
        circle = plt.Circle((cx, cy), r, color=BLUE, alpha=alpha)
        ax.add_patch(circle)

    ax.text(5, 5.2, "PromoFest", fontsize=42, fontweight="bold",
            color="white", ha="center", va="center", alpha=0.95)
    ax.text(5, 4.4, "Sistema de Confirmación de Asistencia",
            fontsize=16, color="#93C5FD", ha="center", va="center")

    # Línea divisoria
    ax.plot([1.5, 8.5], [3.9, 3.9], color=BLUE, lw=1.5, alpha=0.4)

    ax.text(5, 3.3, "Diagramas de Flujo y Arquitectura", fontsize=12,
            color="#D1D5DB", ha="center", va="center")
    ax.text(5, 2.8, "Feria de Promociones 2025", fontsize=10,
            color="#9CA3AF", ha="center", va="center")

    # Índice de diagramas
    items = [
        "①  Flujo de Autenticación (Registro e Inicio de Sesión)",
        "②  Flujo de Confirmación de Asistencia",
        "③  Secuencia Backend — Transacción y Control de Cupo",
        "④  Mecanismo Anti-Overbooking (Concurrencia)",
        "⑤  Patrón Outbox — Notificaciones al Equipo de Ventas",
        "⑥  Panel de Ventas — Flujo del Administrador",
    ]
    for i, item in enumerate(items):
        ax.text(5, 2.0 - i * 0.38, item, fontsize=8.5,
                color="#E5E7EB", ha="center", va="center")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — Flujo de Autenticación
# ═══════════════════════════════════════════════════════════════════════════════

def page_auth(pdf):
    fig, ax = new_fig("① Flujo de Autenticación", "Registro e Inicio de Sesión")

    # ── Columna izquierda: Registro ──────────────────────────
    ax.text(4.2, 10.7, "REGISTRO", fontsize=9, fontweight="bold",
            color=BLUE, ha="center")

    terminal(ax, 4.2, 10.2, "Usuario abre la app")
    arr(ax, 4.2, 9.85, 4.2, 9.35)

    box(ax, 4.2, 9.0, 2.8, 0.6, "Elige \"Crear cuenta\"")
    arr(ax, 4.2, 8.7, 4.2, 8.1)

    box(ax, 4.2, 7.8, 2.8, 0.55, "Ingresa email + contraseña")
    arr(ax, 4.2, 7.52, 4.2, 6.95)

    box(ax, 4.2, 6.65, 2.8, 0.55, "POST /api/auth/register", color=PURPLE)
    arr(ax, 4.2, 6.37, 4.2, 5.75)

    diamond(ax, 4.2, 5.35, 2.8, 0.75, "¿Email ya\nregistrado?")
    arr(ax, 4.2, 4.97, 4.2, 4.4, "No")
    ax.text(5.6, 5.35, "Sí", fontsize=8, color=RED, fontweight="bold")
    arr(ax, 5.55, 5.35, 6.3, 5.35, color=RED)
    box(ax, 7.1, 5.35, 1.6, 0.5, "Error 409\nEmail en uso", color=RED)

    box(ax, 4.2, 4.1, 3.0, 0.55, "Hash bcrypt · Crea usuario\nrole = 'client'")
    arr(ax, 4.2, 3.82, 4.2, 3.3)

    box(ax, 4.2, 3.0, 2.8, 0.55, "Firma JWT\n(userId + email + role)", color=PURPLE)
    arr(ax, 4.2, 2.72, 4.2, 2.1)

    box(ax, 4.2, 1.8, 3.2, 0.55, "Guarda token + user\nen localStorage")
    arr(ax, 4.2, 1.52, 4.2, 0.95)

    terminal(ax, 4.2, 0.65, "→ Redirige según rol", color=GREEN)

    # ── Columna derecha: Login ───────────────────────────────
    ax.text(11.5, 10.7, "INICIO DE SESIÓN", fontsize=9, fontweight="bold",
            color=ORANGE, ha="center")

    terminal(ax, 11.5, 10.2, "Usuario tiene cuenta")
    arr(ax, 11.5, 9.85, 11.5, 9.35)

    box(ax, 11.5, 9.0, 2.8, 0.6, "Ingresa email + contraseña")
    arr(ax, 11.5, 8.7, 11.5, 8.1)

    box(ax, 11.5, 7.8, 2.8, 0.55, "POST /api/auth/login", color=PURPLE)
    arr(ax, 11.5, 7.52, 11.5, 6.95)

    diamond(ax, 11.5, 6.55, 2.8, 0.75, "¿Credenciales\ncorrectas?")
    arr(ax, 11.5, 6.17, 11.5, 5.6, "Sí")
    ax.text(12.95, 6.55, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, 12.9, 6.55, 13.8, 6.55, color=RED)
    box(ax, 14.5, 6.55, 1.6, 0.5, "Error 401\nCredenciales\nincorrectas", color=RED)

    box(ax, 11.5, 5.3, 2.8, 0.55, "Firma JWT\n(userId + email + role)", color=PURPLE)
    arr(ax, 11.5, 5.02, 11.5, 4.45)

    box(ax, 11.5, 4.15, 3.2, 0.55, "Guarda token + user\nen localStorage")
    arr(ax, 11.5, 3.87, 11.5, 3.35)

    diamond(ax, 11.5, 2.95, 2.6, 0.7, "role =\n'admin'?")
    arr(ax, 11.5, 2.6, 11.5, 2.0, "No → /confirm")
    box(ax, 11.5, 1.7, 2.4, 0.5, "Redirige a /confirm\n(ConfirmPage)", color=GREEN)

    ax.text(13.0, 2.95, "Sí → /admin", fontsize=7.5, color=ORANGE, fontweight="bold")
    arr(ax, 12.8, 2.95, 13.9, 2.95, color=ORANGE)
    box(ax, 14.6, 2.95, 2.0, 0.5, "Redirige a /admin\n(AdminPage)", color=ORANGE)

    # Divisor vertical
    ax.plot([8, 8], [0.4, 11.0], color="#D1D5DB", lw=1, ls="--", alpha=0.7)

    # Leyenda
    legend_item(ax, 0.5, 0.7, BLUE, "Proceso")
    legend_item(ax, 2.2, 0.7, AMBER, "Decisión")
    legend_item(ax, 3.9, 0.7, GREEN, "Inicio / Fin / Éxito")
    legend_item(ax, 5.9, 0.7, RED, "Error")
    legend_item(ax, 7.5, 0.7, PURPLE, "API / DB")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 3 — Flujo de Confirmación (perspectiva usuario)
# ═══════════════════════════════════════════════════════════════════════════════

def page_confirm_user(pdf):
    fig, ax = new_fig("② Flujo de Confirmación de Asistencia",
                      "Perspectiva del usuario")

    terminal(ax, 8, 10.7, "Usuario autenticado en /confirm")
    arr(ax, 8, 10.35, 8, 9.75)

    box(ax, 8, 9.45, 4.0, 0.55,
        "Carga en paralelo:\nCatálogo · Estado del evento · Confirmación existente",
        color=PURPLE)
    arr(ax, 8, 9.17, 8, 8.55)

    diamond(ax, 8, 8.15, 3.4, 0.7, "¿Ya confirmó\nanteriormente?")
    # Rama Sí
    ax.text(9.75, 8.15, "Sí", fontsize=8, color=AMBER, fontweight="bold")
    arr(ax, 9.7, 8.15, 12.5, 8.15, color=AMBER)
    box(ax, 13.5, 8.15, 2.4, 0.7,
        "Pantalla\nAlreadyConfirmed\n(resumen de su cupo)", color=AMBER)
    arr(ax, 13.5, 7.8, 13.5, 7.25, color=AMBER)
    terminal(ax, 13.5, 7.0, "Cerrar sesión", color=GRAY)

    # Rama No
    arr(ax, 8, 7.8, 8, 7.2, "No")

    diamond(ax, 8, 6.82, 2.8, 0.65, "¿Evento lleno?")
    ax.text(9.45, 6.82, "Sí", fontsize=8, color=RED, fontweight="bold")
    arr(ax, 9.4, 6.82, 11.2, 6.82, color=RED)
    box(ax, 12.2, 6.82, 2.2, 0.55,
        "Banner: Evento\nalcanzó cupo máximo", color=RED)

    arr(ax, 8, 6.5, 8, 5.9, "No")

    # Paso 1
    ax.text(3.5, 5.7, "PASO 1", fontsize=8, color=BLUE,
            fontweight="bold", ha="center")
    box(ax, 8, 5.55, 5.0, 0.65,
        "Nombre · Apellido · Email (bloqueado al login)\nSelecciona fecha y hora de sesión")
    arr(ax, 8, 5.22, 8, 4.6)

    diamond(ax, 8, 4.22, 2.6, 0.65, "¿Datos\nválidos?")
    arr(ax, 8, 3.89, 8, 3.3, "Sí")
    ax.text(9.35, 4.22, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, 9.3, 4.22, 10.5, 4.22, rad=-0.4, color=RED)
    ax.annotate("", xy=(8 + 2.5, 5.55), xytext=(10.5, 4.22),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.5,
                                connectionstyle="arc3,rad=-0.5"))
    note(ax, 11.2, 4.85, "Muestra errores\nde validación", RED)

    # Paso 2
    ax.text(3.5, 3.1, "PASO 2", fontsize=8, color=GREEN,
            fontweight="bold", ha="center")
    box(ax, 8, 3.0, 5.0, 0.55,
        "Selección de servicios y productos\nDescuentos calculados en tiempo real")
    arr(ax, 8, 2.72, 8, 2.1)

    diamond(ax, 8, 1.72, 2.8, 0.65, "¿Al menos\n1 ítem?")
    arr(ax, 8, 1.39, 8, 0.85, "Sí")
    ax.text(9.45, 1.72, "No", fontsize=8, color=GRAY, fontweight="bold")
    arr(ax, 9.4, 1.72, 11.0, 1.72, color=GRAY)
    note(ax, 12.0, 1.72, "Botón de confirmar\ndisabled", GRAY)

    terminal(ax, 8, 0.55, "POST /api/attendees/confirm  →  Ver diagrama ③", color=PURPLE)

    # Leyenda
    legend_item(ax, 0.3, 0.7, BLUE, "Proceso")
    legend_item(ax, 1.8, 0.7, AMBER, "Decisión")
    legend_item(ax, 3.3, 0.7, GREEN, "Éxito / Inicio")
    legend_item(ax, 4.9, 0.7, RED, "Error / Lleno")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 4 — Secuencia Backend (confirmación)
# ═══════════════════════════════════════════════════════════════════════════════

def page_backend_sequence(pdf):
    fig, ax = new_fig("③ Secuencia Backend — Confirmación",
                      "POST /api/attendees/confirm")

    # Lifelines
    ACTORS = {
        "Frontend\n(React)": 2.0,
        "Express\nAPI":       5.5,
        "Discount\nService":  8.5,
        "PostgreSQL\n(DB)":   12.5,
    }
    COLS = {k: v for k, v in ACTORS.items()}
    COLORS = [BLUE, GREEN, AMBER, PURPLE]

    for (name, x), c in zip(ACTORS.items(), COLORS):
        box(ax, x, 10.7, 1.8, 0.55, name, color=c, fontsize=8)
        ax.plot([x, x], [0.4, 10.42], color=c, lw=1.2, ls="--", alpha=0.4)

    def msg(y, x1, x2, text, color=DARK, ret=False):
        style = "<-" if ret else "->"
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle=style, color=color,
                                   lw=1.5 if not ret else 1.2,
                                   connectionstyle="arc3,rad=0"))
        mx = (x1 + x2) / 2
        ax.text(mx, y + 0.12, text, fontsize=7.5, color=color,
                ha="center", fontweight="bold" if not ret else "normal")

    def note_seq(y, x, text, color=GRAY):
        ax.text(x, y, f"[ {text} ]", fontsize=7, color=color,
                ha="center", style="italic")

    y = 9.9
    msg(y, 2.0, 5.5, "POST /confirm {datos + item_ids}")
    y -= 0.35
    note_seq(y, 5.5, "Middleware: valida JWT", GREEN)
    y -= 0.3
    note_seq(y, 5.5, "Middleware: valida Zod schema", GREEN)
    y -= 0.35
    msg(y, 5.5, 12.5, "SELECT catalog_items WHERE id IN (...)")
    y -= 0.3
    msg(y, 12.5, 5.5, "items[]", ret=True, color=PURPLE)
    y -= 0.35
    msg(y, 5.5, 12.5, "SELECT attendees WHERE email = ?")
    y -= 0.3
    msg(y, 12.5, 5.5, "¿existing?", ret=True, color=PURPLE)
    y -= 0.3
    note_seq(y, 12.5, "409 si ya existe confirmación", RED)
    y -= 0.35
    msg(y, 5.5, 8.5, "calculateDiscounts(items)")
    y -= 0.3
    msg(y, 8.5, 5.5, "{servicesDiscount, productsDiscount}", ret=True, color=AMBER)
    y -= 0.4

    # Bloque de transacción
    tx_top = y + 0.15
    msg(y, 5.5, 12.5, "BEGIN TRANSACTION", color=PURPLE)
    y -= 0.35
    msg(y, 5.5, 12.5, "SELECT event_config FOR UPDATE  ← BLOQUEO")
    y -= 0.3
    msg(y, 12.5, 5.5, "{capacity, confirmed_count}", ret=True, color=PURPLE)
    y -= 0.3
    note_seq(y, 12.5, "409 si cupo agotado", RED)
    y -= 0.35
    msg(y, 5.5, 12.5, "INSERT INTO attendees (...)")
    y -= 0.3
    msg(y, 5.5, 12.5, "INSERT INTO attendee_items (...)")
    y -= 0.3
    msg(y, 5.5, 12.5, "UPDATE event_config SET confirmed_count + 1")
    y -= 0.35
    msg(y, 5.5, 12.5, "COMMIT  — libera el lock", color=GREEN)
    tx_bot = y - 0.1
    # Caja de transacción
    rect = mpatches.FancyBboxPatch((4.6, tx_bot), 8.8, tx_top - tx_bot,
                                   boxstyle="round,pad=0.08",
                                   facecolor="none", edgecolor=PURPLE,
                                   linewidth=1.5, linestyle="--", zorder=2)
    ax.add_patch(rect)
    ax.text(4.65, tx_bot + (tx_top - tx_bot)/2, "Transacción\nDB",
            fontsize=6.5, color=PURPLE, va="center", rotation=90)

    y -= 0.4
    msg(y, 5.5, 12.5, "SELECT attendee + items (respuesta completa)")
    y -= 0.3
    msg(y, 12.5, 5.5, "fullAttendee", ret=True, color=PURPLE)
    y -= 0.35
    note_seq(y, 5.5, "notifySalesTeam() — async, no bloquea", GRAY)
    y -= 0.3
    msg(y, 5.5, 2.0, "201 {attendee, discounts, spots_remaining}", ret=True, color=GREEN)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 5 — Anti-overbooking
# ═══════════════════════════════════════════════════════════════════════════════

def page_overbooking(pdf):
    fig, ax = new_fig("④ Mecanismo Anti-Overbooking",
                      "Control de concurrencia con SELECT FOR UPDATE")

    # Dos carriles: T1 (izquierda) y T2 (derecha)
    T1_X, T2_X, DB_X = 3.5, 10.5, 7.0

    # Encabezados
    box(ax, T1_X, 10.7, 2.8, 0.55, "Transacción 1\n(Usuario A)", color=BLUE)
    box(ax, DB_X, 10.7, 2.5, 0.55, "PostgreSQL\nevent_config (1 cupo)", color=PURPLE)
    box(ax, T2_X, 10.7, 2.8, 0.55, "Transacción 2\n(Usuario B)", color=ORANGE)

    # Lifelines
    for x, c in [(T1_X, BLUE), (DB_X, PURPLE), (T2_X, ORANGE)]:
        ax.plot([x, x], [0.4, 10.42], color=c, lw=1.2, ls="--", alpha=0.35)

    def smsg(y, x1, x2, text, color=DARK, dashed=False):
        ls = (0, (5, 3)) if dashed else "-"
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5,
                                   connectionstyle="arc3,rad=0",
                                   linestyle=ls))
        ax.text((x1+x2)/2, y + 0.13, text, fontsize=7.5, color=color,
                ha="center", fontweight="bold")

    def snote(y, x, text, color=DARK, bg=None):
        if bg:
            rect = FancyBboxPatch((x - 1.8, y - 0.2), 3.6, 0.4,
                                  boxstyle="round,pad=0.05",
                                  facecolor=bg, edgecolor="none", alpha=0.25, zorder=2)
            ax.add_patch(rect)
        ax.text(x, y, text, fontsize=8, color=color,
                ha="center", va="center", fontweight="bold")

    y = 9.9
    smsg(y, T1_X, DB_X, "BEGIN TRANSACTION")
    y -= 0.3
    smsg(y, T2_X, DB_X, "BEGIN TRANSACTION", color=ORANGE)
    y -= 0.5

    smsg(y, T1_X, DB_X, "SELECT ... FOR UPDATE", color=BLUE)
    y -= 0.3
    snote(y, DB_X, "T1 ADQUIERE EL LOCK [LOCKED]", BLUE, bg=BLUE)
    y -= 0.35
    smsg(y, DB_X, T1_X, "spots_remaining = 1  [OK]", color=BLUE, dashed=True)

    y -= 0.4
    smsg(y, T2_X, DB_X, "SELECT ... FOR UPDATE", color=ORANGE)
    y -= 0.3
    snote(y, DB_X, "T2 BLOQUEADA — espera a T1 [WAIT]", ORANGE, bg=ORANGE)

    y -= 0.5
    smsg(y, T1_X, DB_X, "INSERT attendee (Usuario A)", color=BLUE)
    y -= 0.3
    smsg(y, T1_X, DB_X, "UPDATE confirmed_count + 1", color=BLUE)
    y -= 0.3
    smsg(y, T1_X, DB_X, "COMMIT  ->  libera lock", color=GREEN)
    snote(y - 0.28, DB_X, "Lock liberado [UNLOCKED]", GREEN, bg=GREEN)

    y -= 0.7
    snote(y, DB_X, "T2 recibe el lock — lee nueva foto", ORANGE, bg=ORANGE)
    y -= 0.35
    smsg(y, DB_X, T2_X, "spots_remaining = 0  [X]", color=RED, dashed=True)

    y -= 0.35
    snote(y, T2_X, "ROLLBACK", RED, bg=RED)
    y -= 0.3
    ax.text(T2_X, y, "Error 409: Evento lleno", fontsize=8.5,
            color=RED, ha="center", fontweight="bold")

    y -= 0.45
    ax.text(7, y, "Resultado: Solo Usuario A confirmado — cupo nunca superado",
            fontsize=9, color=GREEN, ha="center", fontweight="bold")

    # Nota de SQL
    note_box = FancyBboxPatch((0.3, 0.5), 15.4, 1.0,
                              boxstyle="round,pad=0.12",
                              facecolor="#EFF6FF", edgecolor=BLUE,
                              linewidth=1.5, zorder=2)
    ax.add_patch(note_box)
    ax.text(8, 1.18, "SQL clave dentro de la transacción:", fontsize=8,
            color=BLUE, ha="center", fontweight="bold")
    ax.text(8, 0.82, "SELECT capacity, confirmed_count FROM event_config "
            "WHERE id = 1  FOR UPDATE;",
            fontsize=8.5, color=DARK, ha="center", family="monospace")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 6 — Patrón Outbox (Notificaciones)
# ═══════════════════════════════════════════════════════════════════════════════

def page_outbox(pdf):
    fig, ax = new_fig("⑤ Patrón Outbox — Notificaciones al Equipo de Ventas",
                      "Notificación asíncrona sin bloqueo")

    # Flujo principal (vertical)
    terminal(ax, 8, 10.7, "COMMIT exitoso — Asistente confirmado")
    arr(ax, 8, 10.35, 8, 9.75)

    box(ax, 8, 9.45, 5.0, 0.65,
        "notifySalesTeam(attendee, items)\n[llamada async — no bloquea la respuesta]",
        color=GRAY)
    arr(ax, 8, 9.12, 8, 8.5)

    box(ax, 8, 8.2, 4.5, 0.55,
        "INSERT notification_log\n(status = 'pending', payload = snapshot completo)",
        color=PURPLE)
    arr(ax, 8, 7.92, 8, 7.3)

    # Respuesta al cliente (sale hacia la derecha)
    ax.annotate("", xy=(14.5, 9.45), xytext=(10.5, 9.45),
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=2.0,
                                connectionstyle="arc3,rad=0"))
    box(ax, 14.5, 8.8, 2.5, 1.1,
        "201 al usuario\n\nConfirmación\nno depende de\nla notificación",
        color=GREEN, fontsize=8)
    ax.text(12.5, 9.65, "Respuesta inmediata", fontsize=8,
            color=GREEN, ha="center", fontweight="bold")

    box(ax, 8, 7.0, 4.0, 0.55,
        "simulateSend(payload)\nActual: logger.info (Winston)\nProd.: SendGrid / SQS / Twilio",
        color=BLUE)
    arr(ax, 8, 6.72, 8, 6.1)

    diamond(ax, 8, 5.72, 3.2, 0.75, "¿Envío\nexitoso?")

    # Rama éxito
    arr(ax, 8, 5.35, 8, 4.7, "Sí")
    box(ax, 8, 4.4, 4.5, 0.55,
        "UPDATE notification_log\nstatus = 'sent', sent_at = now()", color=GREEN)
    arr(ax, 8, 4.12, 8, 3.5)
    box(ax, 8, 3.2, 4.2, 0.55,
        "UPDATE attendees\nSET notified_at = now()", color=GREEN)
    arr(ax, 8, 2.92, 8, 2.3)
    terminal(ax, 8, 2.0, "Admin ve ✓ en columna Notif.", color=GREEN)

    # Rama fallo
    ax.text(9.65, 5.72, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, 9.6, 5.72, 12.0, 5.72, color=RED)
    box(ax, 13.5, 5.72, 2.5, 0.7,
        "UPDATE notification_log\nstatus = 'failed'\nlast_error = msg", color=RED)
    arr(ax, 13.5, 5.37, 13.5, 4.7, color=RED)
    box(ax, 13.5, 4.4, 2.8, 0.7,
        "Registro disponible\npara retry manual\no job automático\n(status='failed')",
        color=AMBER)

    # Nota de producción
    note_box = FancyBboxPatch((0.3, 0.5), 15.4, 1.1,
                              boxstyle="round,pad=0.12",
                              facecolor="#FFF7ED", edgecolor=AMBER,
                              linewidth=1.5, zorder=2)
    ax.add_patch(note_box)
    ax.text(8, 1.2, "Migración a producción: reemplazar simulateSend() con llamada real",
            fontsize=8.5, color=AMBER, ha="center", fontweight="bold")
    ax.text(8, 0.82,
            "SendGrid → email | Twilio → SMS/WhatsApp | AWS SQS → cola async"
            " | Slack Webhook → canal de ventas",
            fontsize=8, color=DARK, ha="center")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 7 — Panel de Admin
# ═══════════════════════════════════════════════════════════════════════════════

def page_admin(pdf):
    fig, ax = new_fig("⑥ Panel de Ventas — Flujo del Administrador",
                      "Vista exclusiva role='admin'")

    terminal(ax, 8, 10.7, "Admin hace login con ADMIN_EMAIL / ADMIN_PASSWORD")
    arr(ax, 8, 10.35, 8, 9.75)

    diamond(ax, 8, 9.37, 3.0, 0.72, "role === 'admin'?")
    ax.text(9.55, 9.37, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, 9.5, 9.37, 11.5, 9.37, color=RED)
    box(ax, 13.0, 9.37, 2.4, 0.55,
        "AdminRoute redirige\na /confirm", color=RED)

    arr(ax, 8, 9.01, 8, 8.4, "Sí → /admin")

    box(ax, 8, 8.1, 4.2, 0.55,
        "GET /api/attendees\n(Bearer token requerido, role=admin)", color=PURPLE)
    arr(ax, 8, 7.82, 8, 7.2)

    box(ax, 8, 6.9, 5.0, 0.65,
        "Responde: attendees[] + event{capacity, confirmed_count, spots_remaining}",
        color=PURPLE)
    arr(ax, 8, 6.57, 8, 5.95)

    # Dashboard — 4 KPIs
    ax.text(8, 5.75, "Dashboard — KPIs", fontsize=9, color=ORANGE,
            ha="center", fontweight="bold")
    kpis = [
        (3.5, 5.15, "Confirmados\n/ Capacidad", BLUE),
        (6.3, 5.15, "En filtro\nactual", GRAY),
        (9.1, 5.15, "Servicios\ntotales", GREEN),
        (11.9, 5.15, "Productos\ntotales", AMBER),
    ]
    for x, y, label, c in kpis:
        box(ax, x, y, 2.2, 0.7, label, color=c, fontsize=8)

    # Línea que conecta hacia los filtros
    for x, _, _, _ in kpis:
        arr(ax, x, 4.8, x, 4.35)

    # Filtros
    ax.text(8, 4.15, "Filtros (client-side, sin nueva llamada al API)",
            fontsize=8.5, color=DARK, ha="center", fontweight="bold")
    box(ax, 5.5, 3.75, 3.2, 0.6,
        "Búsqueda por\nnombre o email", color=BLUE, fontsize=8)
    box(ax, 10.5, 3.75, 3.2, 0.6,
        "Filtro por\nfecha de sesión", color=BLUE, fontsize=8)
    arr(ax, 5.5, 3.45, 5.5, 2.9)
    arr(ax, 10.5, 3.45, 10.5, 2.9)
    arr(ax, 5.5, 2.9, 8, 2.9)
    arr(ax, 10.5, 2.9, 8, 2.9)
    arr(ax, 8, 2.9, 8, 2.35)

    # Tabla
    box(ax, 8, 2.0, 11.0, 0.6,
        "Tabla de asistentes: Nombre · Email · Sesión · Servicios · Productos"
        " · Desc. Serv. · Desc. Prod. · Confirmado · Notif. (✓/—)",
        color=ORANGE, fontsize=8)

    # Columna de logout
    arr(ax, 8, 1.7, 8, 1.15)
    terminal(ax, 8, 0.85, "Botón Salir → logout() → localStorage limpiado", color=GRAY)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"Generando diagramas en: {OUTPUT}")
    with PdfPages(OUTPUT) as pdf:
        # Metadata del PDF
        d = pdf.infodict()
        d["Title"]   = "PromoFest — Diagramas de Flujo"
        d["Author"]  = "PromoFest / Feria de Promociones 2025"
        d["Subject"] = "Diagramas técnicos del sistema de confirmación de asistencia"

        page_cover(pdf)
        page_auth(pdf)
        page_confirm_user(pdf)
        page_backend_sequence(pdf)
        page_overbooking(pdf)
        page_outbox(pdf)
        page_admin(pdf)

    print(f"[OK] PDF generado exitosamente: {OUTPUT}")
    print("   7 paginas -- incluye portada y 6 diagramas de flujo")


if __name__ == "__main__":
    main()
