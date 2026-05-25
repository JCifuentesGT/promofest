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
BLUE   = "#3B82F6"
AMBER  = "#D97706"
GREEN  = "#10B981"
RED    = "#EF4444"
PURPLE = "#7C3AED"
GRAY   = "#6B7280"
ORANGE = "#F97316"
DARK   = "#1F2937"
BG     = "#F8FAFC"

# ── Constantes de layout ──────────────────────────────────────────────────────
# Header: y=11.2 a 12.0
# Contenido: y=YBOT a YTOP  (nunca solapar header ni legend/footer)
# Legend: y=YLEG  → rect de y-0.14 a y+0.14
# Footer: y=YFTR
XW     = 16      # xlim
YH     = 12      # ylim
YTOP   = 10.25   # y máx para centros de terminales superiores  (tope real ≈ +0.47 = 10.72 < 11.2)
YBOT   = 2.3     # y mín para centros de terminales inferiores  (base real ≈ -0.47 = 1.83 > 1.5)
YLEG   = 0.65    # centro de leyenda
YFTR   = 0.22    # footer


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def new_fig(title, subtitle="", size=(11, 8.5)):
    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, XW)
    ax.set_ylim(0, YH)
    ax.axis("off")

    # Header
    bar = FancyBboxPatch((0, 11.2), XW, 0.8, boxstyle="square",
                         facecolor=BLUE, edgecolor="none", zorder=5)
    ax.add_patch(bar)
    ax.text(0.4, 11.6, "PromoFest", fontsize=9, color="white",
            va="center", alpha=0.85, zorder=6)
    ax.text(XW / 2, 11.6, title, fontsize=12, fontweight="bold",
            color="white", ha="center", va="center", zorder=6)
    if subtitle:
        ax.text(XW - 0.4, 11.6, subtitle, fontsize=7.5, color="white",
                va="center", ha="right", alpha=0.85, zorder=6)

    # Footer
    ax.text(XW / 2, YFTR,
            "Feria de Promociones 2025 — Documentacion tecnica",
            fontsize=7, color=GRAY, ha="center")
    return fig, ax


def box(ax, x, y, w, h, text, color=BLUE, fontsize=8.5):
    """Rectangulo redondeado con texto blanco centrado."""
    rect = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                           boxstyle="round,pad=0.08",
                           facecolor=color, edgecolor="white",
                           linewidth=2, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4,
            multialignment="center", linespacing=1.35)


def diamond(ax, x, y, w, h, text, color=AMBER, fontsize=8):
    """Rombo de decision."""
    pts = np.array([[x, y + h / 2], [x + w / 2, y],
                    [x, y - h / 2], [x - w / 2, y]])
    poly = plt.Polygon(pts, facecolor=color, edgecolor="white",
                       linewidth=2, zorder=3)
    ax.add_patch(poly)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4, multialignment="center")


def terminal(ax, x, y, text, color=GREEN):
    """Capsula inicio/fin. Extent real +-0.47 en y (rect +-0.32 + pad 0.15)."""
    rect = FancyBboxPatch((x - 1.55, y - 0.32), 3.1, 0.64,
                           boxstyle="round,pad=0.15",
                           facecolor=color, edgecolor="white",
                           linewidth=2, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.5,
            color="white", fontweight="bold", zorder=4,
            multialignment="center", linespacing=1.3)


def terminal_wide(ax, x, y, w, text, color=GREEN, fontsize=8.5):
    """Capsula de ancho personalizado."""
    rect = FancyBboxPatch((x - w / 2, y - 0.32), w, 0.64,
                           boxstyle="round,pad=0.15",
                           facecolor=color, edgecolor="white",
                           linewidth=2, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4,
            multialignment="center", linespacing=1.3)


def arr(ax, x1, y1, x2, y2, label="", color=DARK, lw=1.6, rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw,
                                connectionstyle=f"arc3,rad={rad}"))
    if label:
        ox = 0.2 if x2 >= x1 else -0.2
        oy = 0.15 if y1 == y2 else 0.0
        ax.text((x1 + x2) / 2 + ox, (y1 + y2) / 2 + oy,
                label, fontsize=7.5, color=color,
                style="italic", ha="center", va="center")


def note(ax, x, y, text, color=GRAY):
    ax.text(x, y, text, fontsize=7.5, color=color,
            style="italic", ha="center", va="center",
            multialignment="center")


def legend_item(ax, x, y, color, label):
    rect = FancyBboxPatch((x, y - 0.14), 0.38, 0.28,
                           boxstyle="round,pad=0.04",
                           facecolor=color, edgecolor="none", zorder=6)
    ax.add_patch(rect)
    ax.text(x + 0.52, y, label, fontsize=7.5, color=DARK, va="center", zorder=6)


def note_box(ax, y0, h, title, body, bc=BLUE, fc="#EFF6FF"):
    """Caja de nota al pie (separada del contenido del diagrama)."""
    rect = FancyBboxPatch((0.4, y0), XW - 0.8, h,
                           boxstyle="round,pad=0.12",
                           facecolor=fc, edgecolor=bc,
                           linewidth=1.5, zorder=2)
    ax.add_patch(rect)
    ax.text(XW / 2, y0 + h - 0.25, title,
            fontsize=8.5, color=bc, ha="center", fontweight="bold", zorder=3)
    ax.text(XW / 2, y0 + 0.3, body,
            fontsize=8, color=DARK, ha="center", va="bottom", zorder=3,
            multialignment="center")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGINA 1 — Portada
# ═══════════════════════════════════════════════════════════════════════════════

def page_cover(pdf):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(DARK)
    ax.set_facecolor(DARK)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    for cx, cy, r, alpha in [(1, 6, 2, 0.07), (9, 1, 2.5, 0.05), (5, 3.5, 4, 0.04)]:
        ax.add_patch(plt.Circle((cx, cy), r, color=BLUE, alpha=alpha))

    ax.text(5, 5.2, "PromoFest", fontsize=42, fontweight="bold",
            color="white", ha="center", va="center")
    ax.text(5, 4.4, "Sistema de Confirmacion de Asistencia",
            fontsize=16, color="#93C5FD", ha="center", va="center")
    ax.plot([1.5, 8.5], [3.9, 3.9], color=BLUE, lw=1.5, alpha=0.4)
    ax.text(5, 3.3, "Diagramas de Flujo y Arquitectura",
            fontsize=12, color="#D1D5DB", ha="center", va="center")
    ax.text(5, 2.8, "Feria de Promociones 2025",
            fontsize=10, color="#9CA3AF", ha="center", va="center")

    items = [
        "1.  Flujo de Autenticacion (Registro e Inicio de Sesion)",
        "2.  Flujo de Confirmacion de Asistencia",
        "3.  Secuencia Backend — Transaccion y Control de Cupo",
        "4.  Mecanismo Anti-Overbooking (Concurrencia)",
        "5.  Patron Outbox — Notificaciones al Equipo de Ventas",
        "6.  Panel de Ventas — Flujo del Administrador",
    ]
    for i, item in enumerate(items):
        ax.text(5, 2.0 - i * 0.38, item, fontsize=9,
                color="#E5E7EB", ha="center", va="center")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGINA 2 — Flujo de Autenticacion
# (Dos columnas: Registro izq, Login der)
# Zona segura: y in [YBOT=2.3, YTOP=10.25]
# ═══════════════════════════════════════════════════════════════════════════════

def page_auth(pdf):
    fig, ax = new_fig("1. Flujo de Autenticacion", "Registro e Inicio de Sesion")

    LX = 4.2    # centro columna izquierda
    RX = 11.8   # centro columna derecha
    BW = 3.2    # ancho de cajas principales

    # ── Divisor vertical ────────────────────────────────────────────────────
    ax.plot([8, 8], [1.0, 11.0], color="#D1D5DB", lw=1, ls="--", alpha=0.7)

    # ══════════════════════════════════════════════════════
    # COLUMNA IZQUIERDA — REGISTRO
    # ══════════════════════════════════════════════════════
    ax.text(LX, 10.8, "REGISTRO", fontsize=9, fontweight="bold",
            color=BLUE, ha="center")

    terminal(ax, LX, YTOP, "Usuario abre la app")
    arr(ax, LX, YTOP - 0.47, LX, 9.55)

    box(ax, LX, 9.25, BW, 0.55, "Elige \"Crear cuenta\"")
    arr(ax, LX, 8.97, LX, 8.55)

    box(ax, LX, 8.25, BW, 0.55, "Ingresa email\n+ contrasena")
    arr(ax, LX, 7.97, LX, 7.55)

    box(ax, LX, 7.25, BW, 0.55, "POST /api/auth/register", color=PURPLE)
    arr(ax, LX, 6.97, LX, 6.4)

    diamond(ax, LX, 6.0, 3.0, 0.72, "Email ya\nregistrado?")
    # Rama Si → error
    ax.text(LX + 1.68, 6.2, "Si", fontsize=8, color=RED, fontweight="bold")
    arr(ax, LX + 1.5, 6.0, LX + 2.1, 6.0, color=RED)
    box(ax, LX + 3.1, 6.0, 1.9, 0.7, "Error 409\nEmail en uso", color=RED, fontsize=8)
    # Rama No ↓
    arr(ax, LX, 5.64, LX, 5.1, "No")

    box(ax, LX, 4.8, BW, 0.55, "Hash bcrypt · Crea usuario\nrole = 'client'")
    arr(ax, LX, 4.52, LX, 4.1)

    box(ax, LX, 3.8, BW, 0.55, "Firma JWT\n(userId + email + role)", color=PURPLE)
    arr(ax, LX, 3.52, LX, 3.05)

    box(ax, LX, 2.75, BW, 0.55, "Guarda token en localStorage")
    arr(ax, LX, 2.47, LX, YBOT)

    terminal(ax, LX, YBOT, "Redirige segun rol")

    # ══════════════════════════════════════════════════════
    # COLUMNA DERECHA — LOGIN
    # ══════════════════════════════════════════════════════
    ax.text(RX, 10.8, "INICIO DE SESION", fontsize=9, fontweight="bold",
            color=ORANGE, ha="center")

    terminal(ax, RX, YTOP, "Usuario tiene cuenta")
    arr(ax, RX, YTOP - 0.47, RX, 9.55)

    box(ax, RX, 9.25, BW, 0.55, "Ingresa email\n+ contrasena")
    arr(ax, RX, 8.97, RX, 8.55)

    box(ax, RX, 8.25, BW, 0.55, "POST /api/auth/login", color=PURPLE)
    arr(ax, RX, 7.97, RX, 7.35)

    diamond(ax, RX, 6.95, 3.0, 0.72, "Credenciales\ncorrectas?")
    # Rama No → error (derecha, acotada al borde)
    ax.text(RX + 1.7, 7.15, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, RX + 1.5, 6.95, RX + 2.1, 6.95, color=RED)
    box(ax, RX + 2.9, 6.95, 1.8, 0.8,
        "Error 401\nCredenciales\nincorrectas", color=RED, fontsize=7.5)
    # Rama Si ↓
    arr(ax, RX, 6.59, RX, 6.05, "Si")

    box(ax, RX, 5.75, BW, 0.55, "Firma JWT\n(userId + email + role)", color=PURPLE)
    arr(ax, RX, 5.47, RX, 5.0)

    box(ax, RX, 4.7, BW, 0.55, "Guarda token en localStorage")
    arr(ax, RX, 4.42, RX, 3.85)

    diamond(ax, RX, 3.45, 2.8, 0.72, "role =\n'admin'?")
    # Rama Si → /admin
    ax.text(RX + 1.5, 3.65, "Si", fontsize=8, color=ORANGE, fontweight="bold")
    arr(ax, RX + 1.4, 3.45, RX + 2.0, 3.45, color=ORANGE)
    box(ax, RX + 3.0, 3.45, 2.1, 0.55,
        "Redirige a /admin\n(AdminPage)", color=ORANGE, fontsize=8)
    # Rama No ↓ → /confirm
    arr(ax, RX, 3.09, RX, 2.65, "No")
    box(ax, RX, 2.4, 3.0, 0.45,
        "Redirige a /confirm (ConfirmPage)", color=GREEN, fontsize=8)

    # ── Leyenda ────────────────────────────────────────────────────────────
    legend_item(ax, 0.4,  YLEG, BLUE,   "Proceso")
    legend_item(ax, 2.2,  YLEG, AMBER,  "Decision")
    legend_item(ax, 4.1,  YLEG, GREEN,  "Inicio / Fin")
    legend_item(ax, 5.9,  YLEG, RED,    "Error")
    legend_item(ax, 7.5,  YLEG, PURPLE, "API / DB")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGINA 3 — Flujo de Confirmacion (perspectiva usuario)
# ═══════════════════════════════════════════════════════════════════════════════

def page_confirm_user(pdf):
    fig, ax = new_fig("2. Flujo de Confirmacion de Asistencia",
                      "Perspectiva del usuario")

    CX = 7.5    # centro principal
    BW = 4.8    # ancho cajas principales

    terminal_wide(ax, CX, YTOP, BW + 1.2,
                  "Usuario autenticado en /confirm")
    arr(ax, CX, YTOP - 0.47, CX, 9.55)

    box(ax, CX, 9.25, BW, 0.65,
        "Carga en paralelo:\nCatalogo · Estado evento · Confirmacion existente",
        color=PURPLE)
    arr(ax, CX, 8.92, CX, 8.35)

    diamond(ax, CX, 7.95, 3.2, 0.72, "Ya confirmo\nanteriormente?")
    # Rama Si → AlreadyConfirmed
    ax.text(CX + 1.75, 8.2, "Si", fontsize=8, color=AMBER, fontweight="bold")
    arr(ax, CX + 1.6, 7.95, CX + 2.2, 7.95, color=AMBER)
    box(ax, CX + 3.8, 7.95, 2.9, 0.8,
        "Pantalla AlreadyConfirmed\n(resumen de su cupo)", color=AMBER, fontsize=8)
    arr(ax, CX + 3.8, 7.55, CX + 3.8, 7.1, color=AMBER)
    box(ax, CX + 3.8, 6.85, 2.0, 0.45,
        "Cerrar sesion", color=GRAY, fontsize=8)
    # Rama No ↓
    arr(ax, CX, 7.59, CX, 7.05, "No")

    diamond(ax, CX, 6.65, 2.8, 0.68, "Evento lleno?")
    # Rama Si → banner
    ax.text(CX + 1.55, 6.9, "Si", fontsize=8, color=RED, fontweight="bold")
    arr(ax, CX + 1.4, 6.65, CX + 2.0, 6.65, color=RED)
    box(ax, CX + 3.6, 6.65, 2.8, 0.65,
        "Banner: Evento\nalcanzo cupo maximo", color=RED, fontsize=8)
    # Rama No ↓
    arr(ax, CX, 6.31, CX, 5.75, "No")

    # ── Paso 1 ──────────────────────────────────────────────────────────────
    ax.text(1.8, 5.65, "PASO 1", fontsize=8.5, color=BLUE,
            fontweight="bold", ha="center")
    box(ax, CX, 5.45, BW, 0.65,
        "Nombre · Apellido · Email (bloqueado)\nSelecciona fecha y hora de sesion")
    arr(ax, CX, 5.12, CX, 4.55)

    diamond(ax, CX, 4.15, 2.6, 0.68, "Datos\nvalidos?")
    # Rama No → bucle de vuelta a la caja (error validacion)
    ax.text(CX + 1.4, 4.35, "No", fontsize=8, color=RED, fontweight="bold")
    ax.annotate("", xy=(CX + BW / 2, 5.45), xytext=(CX + 1.3, 4.15),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.4,
                                connectionstyle="arc3,rad=-0.4"))
    note(ax, CX + 3.8, 4.85, "Muestra errores\nde validacion", RED)
    # Rama Si ↓
    arr(ax, CX, 3.81, CX, 3.25, "Si")

    # ── Paso 2 ──────────────────────────────────────────────────────────────
    ax.text(1.8, 3.15, "PASO 2", fontsize=8.5, color=GREEN,
            fontweight="bold", ha="center")
    box(ax, CX, 2.95, BW, 0.55,
        "Seleccion de servicios y productos\nDescuentos calculados en tiempo real")
    arr(ax, CX, 2.67, CX, 2.1)

    diamond(ax, CX, 1.7, 2.6, 0.68, "Al menos\n1 item?")
    # Rama No → boton disabled
    ax.text(CX + 1.4, 1.88, "No", fontsize=8, color=GRAY, fontweight="bold")
    arr(ax, CX + 1.3, 1.7, CX + 2.8, 1.7, color=GRAY)
    note(ax, CX + 4.1, 1.7, "Boton Confirmar\ndisabled", GRAY)

    # Flecha Si hacia abajo hacia el terminal de abajo
    arr(ax, CX, 1.36, CX, YBOT + 0.47, "Si")
    terminal_wide(ax, CX, YBOT, BW + 0.4,
                  "POST /api/attendees/confirm  ->  Ver diagrama 3",
                  color=PURPLE)

    # ── Leyenda ─────────────────────────────────────────────────────────────
    legend_item(ax, 0.4, YLEG, BLUE,   "Proceso")
    legend_item(ax, 2.2, YLEG, AMBER,  "Decision")
    legend_item(ax, 4.1, YLEG, GREEN,  "Exito / Inicio")
    legend_item(ax, 6.0, YLEG, RED,    "Error / Lleno")
    legend_item(ax, 7.8, YLEG, GRAY,   "Inactivo")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGINA 4 — Secuencia Backend (confirmacion)
# Actores: Frontend | Express | Discount | PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════

def page_backend_sequence(pdf):
    fig, ax = new_fig("3. Secuencia Backend — Confirmacion",
                      "POST /api/attendees/confirm")

    # Lifelines — posicionados para que las flechas no crucen cajas de actores
    # Frontend(1.8) → Express(5.5) → PostgreSQL(10.5) y Discount(14.5)
    A = {"Frontend\n(React)": 1.8,
         "Express\nAPI":       5.5,
         "PostgreSQL\n(DB)":   10.5,
         "Discount\nService":  14.5}
    COLS = [BLUE, GREEN, PURPLE, AMBER]

    top_y = YTOP  # 10.25
    for (name, x), c in zip(A.items(), COLS):
        box(ax, x, top_y, 2.2, 0.55, name, color=c, fontsize=8)
        ax.plot([x, x], [0.5, top_y - 0.28], color=c, lw=1.2, ls="--", alpha=0.35)

    FX  = A["Frontend\n(React)"]
    EX  = A["Express\nAPI"]
    DBX = A["PostgreSQL\n(DB)"]
    DSX = A["Discount\nService"]

    def msg(y, x1, x2, text, color=DARK, ret=False):
        style = "<-" if ret else "->"
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle=style, color=color, lw=1.5,
                                   connectionstyle="arc3,rad=0"))
        mx = (x1 + x2) / 2
        ax.text(mx, y + 0.13, text, fontsize=7, color=color,
                ha="center", fontweight="bold" if not ret else "normal")

    def note_seq(y, x, text, color=GRAY):
        ax.text(x, y, f"[ {text} ]", fontsize=6.8, color=color,
                ha="center", style="italic")

    y = top_y - 0.55
    msg(y, FX, EX, "POST /confirm  {datos + item_ids}")
    y -= 0.32
    note_seq(y, EX, "Middleware: valida JWT", GREEN)
    y -= 0.27
    note_seq(y, EX, "Middleware: valida Zod schema", GREEN)
    y -= 0.35
    msg(y, EX, DBX, "SELECT catalog_items WHERE id IN (...)")
    y -= 0.28
    msg(y, DBX, EX, "items[]", ret=True, color=PURPLE)
    y -= 0.33
    msg(y, EX, DBX, "SELECT attendees WHERE email = ?")
    y -= 0.28
    msg(y, DBX, EX, "existing?", ret=True, color=PURPLE)
    y -= 0.27
    note_seq(y, DBX, "409 si ya existe confirmacion", RED)
    y -= 0.35
    # Discount Service — flecha va mas alla de PostgreSQL
    msg(y, EX, DSX, "calculateDiscounts(items)", color=AMBER)
    y -= 0.28
    msg(y, DSX, EX, "{servicesDiscount, productsDiscount}", ret=True, color=AMBER)
    y -= 0.38

    # Bloque de transaccion
    tx_top = y + 0.15
    msg(y, EX, DBX, "BEGIN TRANSACTION", color=PURPLE)
    y -= 0.32
    msg(y, EX, DBX, "SELECT event_config FOR UPDATE  <- BLOQUEO")
    y -= 0.27
    msg(y, DBX, EX, "{capacity, confirmed_count}", ret=True, color=PURPLE)
    y -= 0.27
    note_seq(y, DBX, "409 si cupo agotado", RED)
    y -= 0.33
    msg(y, EX, DBX, "INSERT INTO attendees (...)")
    y -= 0.27
    msg(y, EX, DBX, "INSERT INTO attendee_items (...)")
    y -= 0.27
    msg(y, EX, DBX, "UPDATE event_config SET confirmed_count + 1")
    y -= 0.33
    msg(y, EX, DBX, "COMMIT  — libera el lock", color=GREEN)
    tx_bot = y - 0.1

    # Marco de transaccion
    rect = mpatches.FancyBboxPatch(
        (EX - 1.0, tx_bot), DBX - EX + 2.0, tx_top - tx_bot,
        boxstyle="round,pad=0.08",
        facecolor="none", edgecolor=PURPLE,
        linewidth=1.5, linestyle="--", zorder=2)
    ax.add_patch(rect)
    ax.text(EX - 0.95, (tx_top + tx_bot) / 2, "Tx\nDB",
            fontsize=6.5, color=PURPLE, va="center", rotation=90)

    y -= 0.38
    msg(y, EX, DBX, "SELECT attendee + items (respuesta completa)")
    y -= 0.27
    msg(y, DBX, EX, "fullAttendee", ret=True, color=PURPLE)
    y -= 0.33
    note_seq(y, EX, "notifySalesTeam() — async, no bloquea", GRAY)
    y -= 0.28
    msg(y, EX, FX, "201 {attendee, discounts, spots_remaining}", ret=True, color=GREEN)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGINA 5 — Anti-overbooking (concurrencia)
# ═══════════════════════════════════════════════════════════════════════════════

def page_overbooking(pdf):
    fig, ax = new_fig("4. Mecanismo Anti-Overbooking",
                      "Control de concurrencia con SELECT FOR UPDATE")

    T1X = 3.5
    DBX = 8.0
    T2X = 12.5

    box(ax, T1X, YTOP, 3.0, 0.55, "Transaccion 1\n(Usuario A)", color=BLUE)
    box(ax, DBX, YTOP, 3.2, 0.55, "PostgreSQL\nevent_config (1 cupo)", color=PURPLE)
    box(ax, T2X, YTOP, 3.0, 0.55, "Transaccion 2\n(Usuario B)", color=ORANGE)

    for x, c in [(T1X, BLUE), (DBX, PURPLE), (T2X, ORANGE)]:
        ax.plot([x, x], [1.5, YTOP - 0.28], color=c, lw=1.2, ls="--", alpha=0.35)

    def smsg(y, x1, x2, text, color=DARK, dashed=False):
        ls_style = (0, (5, 3)) if dashed else "-"
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5,
                                   connectionstyle="arc3,rad=0",
                                   linestyle=ls_style))
        ax.text((x1 + x2) / 2, y + 0.14, text, fontsize=7.5, color=color,
                ha="center", fontweight="bold")

    def snote(y, x, text, color=DARK, bg=None):
        if bg:
            rect = FancyBboxPatch((x - 2.0, y - 0.22), 4.0, 0.44,
                                  boxstyle="round,pad=0.05",
                                  facecolor=bg, edgecolor="none",
                                  alpha=0.22, zorder=2)
            ax.add_patch(rect)
        ax.text(x, y, text, fontsize=7.5, color=color,
                ha="center", va="center", fontweight="bold")

    y = YTOP - 0.55
    smsg(y, T1X, DBX, "BEGIN TRANSACTION")
    y -= 0.3
    smsg(y, T2X, DBX, "BEGIN TRANSACTION", color=ORANGE)
    y -= 0.48

    smsg(y, T1X, DBX, "SELECT ... FOR UPDATE", color=BLUE)
    y -= 0.3
    snote(y, DBX, "T1 ADQUIERE EL LOCK  [LOCKED]", BLUE, bg=BLUE)
    y -= 0.35
    smsg(y, DBX, T1X, "spots_remaining = 1  [OK]", color=BLUE, dashed=True)

    y -= 0.42
    smsg(y, T2X, DBX, "SELECT ... FOR UPDATE", color=ORANGE)
    y -= 0.3
    snote(y, DBX, "T2 BLOQUEADA — espera a T1  [WAIT]", ORANGE, bg=ORANGE)

    y -= 0.5
    smsg(y, T1X, DBX, "INSERT attendee (Usuario A)", color=BLUE)
    y -= 0.3
    smsg(y, T1X, DBX, "UPDATE confirmed_count + 1", color=BLUE)
    y -= 0.3
    smsg(y, T1X, DBX, "COMMIT  — libera lock", color=GREEN)
    snote(y - 0.3, DBX, "Lock liberado  [UNLOCKED]", GREEN, bg=GREEN)

    y -= 0.68
    snote(y, DBX, "T2 recibe el lock — lee nueva foto", ORANGE, bg=ORANGE)
    y -= 0.35
    smsg(y, DBX, T2X, "spots_remaining = 0  [X]", color=RED, dashed=True)

    y -= 0.35
    snote(y, T2X, "ROLLBACK", RED, bg=RED)
    y -= 0.32
    ax.text(T2X, y, "Error 409: Evento lleno", fontsize=8.5,
            color=RED, ha="center", fontweight="bold")

    y -= 0.45
    ax.text(DBX, y, "Resultado: Solo Usuario A confirmado — cupo nunca superado",
            fontsize=9, color=GREEN, ha="center", fontweight="bold")

    # Nota SQL al pie (por encima de footer y legend)
    note_box(ax, 0.8, 0.9,
             "SQL clave dentro de la transaccion:",
             "SELECT capacity, confirmed_count  FROM event_config  WHERE id = 1  FOR UPDATE;",
             bc=BLUE, fc="#EFF6FF")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGINA 6 — Patron Outbox (Notificaciones)
# ═══════════════════════════════════════════════════════════════════════════════

def page_outbox(pdf):
    fig, ax = new_fig("5. Patron Outbox — Notificaciones al Equipo de Ventas",
                      "Notificacion asincrona sin bloqueo")

    CX  = 7.0   # centro del flujo principal
    RBX = 13.0  # centro cajas de error/retry (lado derecho)
    BW  = 4.6

    terminal_wide(ax, CX, YTOP, BW,
                  "COMMIT exitoso — Asistente confirmado")
    arr(ax, CX, YTOP - 0.47, CX, 9.55)

    box(ax, CX, 9.25, BW, 0.65,
        "notifySalesTeam(attendee, items)\n[llamada async — no bloquea la respuesta]",
        color=GRAY)

    # Flecha de respuesta inmediata al usuario (sale a la derecha del bloque async)
    ax.annotate("", xy=(RBX + 0.5, 9.25), xytext=(CX + BW / 2, 9.25),
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=2.0,
                                connectionstyle="arc3,rad=0"))
    box(ax, RBX + 1.5, 8.7, 2.4, 1.0,
        "201 al usuario\n\nConfirmacion no\ndepende de la\nnotificacion",
        color=GREEN, fontsize=7.5)
    ax.text(RBX + 0.2, 9.5, "Respuesta\ninmediata",
            fontsize=7.5, color=GREEN, ha="center", fontweight="bold")

    arr(ax, CX, 8.92, CX, 8.35)

    box(ax, CX, 8.05, BW, 0.55,
        "INSERT notification_log\n(status = 'pending', payload = snapshot completo)",
        color=PURPLE)
    arr(ax, CX, 7.77, CX, 7.2)

    box(ax, CX, 6.9, BW, 0.65,
        "simulateSend(payload)\nActual: logger.info (Winston)\nProd.: SendGrid / SQS / Twilio",
        color=BLUE, fontsize=8)
    arr(ax, CX, 6.57, CX, 6.0)

    diamond(ax, CX, 5.6, 3.0, 0.72, "Envio\nexitoso?")

    # ── Rama Exito (Si ↓) ───────────────────────────────────────────────────
    arr(ax, CX, 5.24, CX, 4.7, "Si")
    box(ax, CX, 4.4, BW, 0.55,
        "UPDATE notification_log\nstatus = 'sent',  sent_at = now()", color=GREEN)
    arr(ax, CX, 4.12, CX, 3.6)
    box(ax, CX, 3.3, BW, 0.55,
        "UPDATE attendees  SET notified_at = now()", color=GREEN)
    arr(ax, CX, 3.02, CX, YBOT + 0.47)
    terminal_wide(ax, CX, YBOT, BW,
                  "Admin ve marca [OK] en columna Notif.", color=GREEN)

    # ── Rama Fallo (No →) ───────────────────────────────────────────────────
    ax.text(CX + 1.65, 5.8, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, CX + 1.5, 5.6, RBX - 1.3, 5.6, color=RED)
    box(ax, RBX, 5.6, 3.1, 0.75,
        "UPDATE notification_log\nstatus = 'failed'\nlast_error = msg",
        color=RED, fontsize=8)
    arr(ax, RBX, 5.22, RBX, 4.6, color=RED)
    box(ax, RBX, 4.3, 3.2, 0.75,
        "Registro disponible\npara retry manual\no job automatico (status='failed')",
        color=AMBER, fontsize=7.5)

    # Nota de produccion (por encima del footer)
    note_box(ax, 0.8, 0.85,
             "Migracion a produccion: reemplazar simulateSend() con llamada real",
             "SendGrid -> email  |  Twilio -> SMS/WhatsApp  |  AWS SQS -> cola async  |  Slack Webhook -> canal ventas",
             bc=AMBER, fc="#FFF7ED")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGINA 7 — Panel de Ventas (Admin)
# ═══════════════════════════════════════════════════════════════════════════════

def page_admin(pdf):
    fig, ax = new_fig("6. Panel de Ventas — Flujo del Administrador",
                      "Vista exclusiva role='admin'")

    CX = 7.5
    BW = 5.0

    terminal_wide(ax, CX, YTOP, BW,
                  "Admin hace login con ADMIN_EMAIL / ADMIN_PASSWORD")
    arr(ax, CX, YTOP - 0.47, CX, 9.55)

    diamond(ax, CX, 9.15, 3.0, 0.72, "role === 'admin'?")
    # Rama No → redirige a /confirm
    ax.text(CX + 1.65, 9.38, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, CX + 1.5, 9.15, CX + 2.2, 9.15, color=RED)
    box(ax, CX + 3.9, 9.15, 2.8, 0.65,
        "AdminRoute redirige\na /confirm", color=RED, fontsize=8)
    # Rama Si ↓
    arr(ax, CX, 8.79, CX, 8.25, "Si → /admin")

    box(ax, CX, 7.95, BW, 0.55,
        "GET /api/attendees\n(Bearer token requerido, role=admin)", color=PURPLE)
    arr(ax, CX, 7.67, CX, 7.1)

    box(ax, CX, 6.8, BW, 0.65,
        "Responde: attendees[ ] +\nevent {capacity, confirmed_count, spots_remaining}",
        color=PURPLE)
    arr(ax, CX, 6.47, CX, 5.9)

    # Dashboard KPIs
    ax.text(CX, 5.7, "Dashboard — KPIs", fontsize=9, color=ORANGE,
            ha="center", fontweight="bold")
    kpis = [
        (3.0,  5.2, "Confirmados\n/ Capacidad", BLUE),
        (6.0,  5.2, "En filtro\nactual",        GRAY),
        (9.0,  5.2, "Servicios\ntotales",       GREEN),
        (12.0, 5.2, "Productos\ntotales",       AMBER),
    ]
    for x, y, label, c in kpis:
        box(ax, x, y, 2.4, 0.75, label, color=c, fontsize=8)
        arr(ax, x, 4.82, x, 4.4)

    # Etiqueta filtros
    ax.text(CX, 4.2, "Filtros client-side (sin nueva llamada al API)",
            fontsize=8.5, color=DARK, ha="center", fontweight="bold")

    box(ax, 4.5, 3.8, 3.4, 0.6, "Busqueda por\nnombre o email", color=BLUE, fontsize=8)
    box(ax, 10.5, 3.8, 3.4, 0.6, "Filtro por\nfecha de sesion", color=BLUE, fontsize=8)
    arr(ax, 4.5, 3.5, 4.5, 3.1)
    arr(ax, 10.5, 3.5, 10.5, 3.1)
    arr(ax, 4.5, 3.1, CX, 3.1)
    arr(ax, 10.5, 3.1, CX, 3.1)
    arr(ax, CX, 3.1, CX, 2.75)

    # Tabla de asistentes
    box(ax, CX, 2.45, 12.5, 0.55,
        "Tabla: Nombre · Email · Sesion · Servicios · Productos"
        " · Desc. Srv · Desc. Prod · Fecha · Notif.",
        color=ORANGE, fontsize=7.8)

    arr(ax, CX, 2.17, CX, YBOT + 0.47)
    terminal_wide(ax, CX, YBOT, BW,
                  "Boton Salir -> logout() -> localStorage limpiado", color=GRAY)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"Generando diagramas en: {OUTPUT}")
    with PdfPages(OUTPUT) as pdf:
        d = pdf.infodict()
        d["Title"]   = "PromoFest — Diagramas de Flujo"
        d["Author"]  = "PromoFest / Feria de Promociones 2025"
        d["Subject"] = "Diagramas tecnicos del sistema de confirmacion de asistencia"

        page_cover(pdf)
        page_auth(pdf)
        page_confirm_user(pdf)
        page_backend_sequence(pdf)
        page_overbooking(pdf)
        page_outbox(pdf)
        page_admin(pdf)

    print(f"[OK] PDF generado: {OUTPUT}")
    print("     7 paginas -- portada + 6 diagramas")


if __name__ == "__main__":
    main()
