#!/usr/bin/env python3
"""
PromoFest — Generador de diagramas de flujo (PDF)
Uso: pip install matplotlib && python docs/generate_diagrams.py
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

BLUE   = "#3B82F6"
AMBER  = "#D97706"
GREEN  = "#10B981"
RED    = "#EF4444"
PURPLE = "#7C3AED"
GRAY   = "#6B7280"
ORANGE = "#F97316"
DARK   = "#1F2937"
BG     = "#F8FAFC"

# ── Layout global ──────────────────────────────────────────────────────────────
# xlim=14 da 0.609 in/unit (vs 0.533 con 16) → caben textos mas largos
XW    = 14      # xlim
YH    = 12      # ylim
YTOP  = 10.25   # y max contenido  (tope real ≈ y+0.47=10.72 < header 11.2)
YBOT  = 1.8     # y min contenido  (base real ≈ y-0.47=1.33 > legend 0.64)
YLEG  = 0.50    # centro leyenda
YFTR  = 0.20    # footer


# ── Primitivas ─────────────────────────────────────────────────────────────────

def new_fig(title, subtitle="", size=(11, 8.5)):
    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, XW)
    ax.set_ylim(0, YH)
    ax.axis("off")
    # Header
    ax.add_patch(FancyBboxPatch((0, 11.2), XW, 0.8, boxstyle="square",
                                facecolor=BLUE, edgecolor="none", zorder=5))
    ax.text(0.35, 11.6, "PromoFest", fontsize=9, color="white",
            va="center", alpha=0.85, zorder=6)
    ax.text(XW / 2, 11.6, title, fontsize=12, fontweight="bold",
            color="white", ha="center", va="center", zorder=6)
    if subtitle:
        ax.text(XW - 0.35, 11.6, subtitle, fontsize=7.5, color="white",
                va="center", ha="right", alpha=0.85, zorder=6)
    # Footer
    ax.text(XW / 2, YFTR, "Feria de Promociones 2025 — Documentacion tecnica",
            fontsize=7, color=GRAY, ha="center")
    return fig, ax


def box(ax, x, y, w, h, text, color=BLUE, fontsize=8.5):
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle="round,pad=0.08",
                                facecolor=color, edgecolor="white",
                                linewidth=2, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4,
            multialignment="center", linespacing=1.35)


def diamond(ax, x, y, w, h, text, color=AMBER, fontsize=8):
    pts = np.array([[x, y+h/2], [x+w/2, y], [x, y-h/2], [x-w/2, y]])
    ax.add_patch(plt.Polygon(pts, facecolor=color, edgecolor="white",
                             linewidth=2, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4, multialignment="center")


def terminal(ax, x, y, w, text, color=GREEN, fontsize=8.5):
    """Capsula de ancho w. Extent real: +-0.47 en y (rect+-0.32 + pad 0.15)."""
    ax.add_patch(FancyBboxPatch((x - w/2, y - 0.32), w, 0.64,
                                boxstyle="round,pad=0.15",
                                facecolor=color, edgecolor="white",
                                linewidth=2, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4,
            multialignment="center", linespacing=1.3)


def arr(ax, x1, y1, x2, y2, label="", color=DARK, lw=1.6, rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw,
                                connectionstyle=f"arc3,rad={rad}"))
    if label:
        ox = 0.18 if x2 >= x1 else -0.18
        oy = 0.14 if y1 == y2 else 0.0
        ax.text((x1+x2)/2 + ox, (y1+y2)/2 + oy, label,
                fontsize=7.5, color=color, style="italic",
                ha="center", va="center")


def note(ax, x, y, text, color=GRAY):
    ax.text(x, y, text, fontsize=7.5, color=color, style="italic",
            ha="center", va="center", multialignment="center")


def leg(ax, x, color, label):
    ax.add_patch(FancyBboxPatch((x, YLEG-0.14), 0.38, 0.28,
                                boxstyle="round,pad=0.04",
                                facecolor=color, edgecolor="none", zorder=6))
    ax.text(x+0.50, YLEG, label, fontsize=7.5, color=DARK, va="center", zorder=6)


def note_box(ax, y0, h, title_txt, body_txt, bc=BLUE, fc="#EFF6FF"):
    ax.add_patch(FancyBboxPatch((0.35, y0), XW-0.7, h,
                                boxstyle="round,pad=0.1",
                                facecolor=fc, edgecolor=bc,
                                linewidth=1.5, zorder=2))
    ax.text(XW/2, y0+h-0.24, title_txt,
            fontsize=8.5, color=bc, ha="center", fontweight="bold", zorder=3)
    ax.text(XW/2, y0+0.28, body_txt,
            fontsize=7.8, color=DARK, ha="center", va="bottom", zorder=3,
            multialignment="center")


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA 1 — Portada
# ══════════════════════════════════════════════════════════════════════════════

def page_cover(pdf):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(DARK)
    ax.set_facecolor(DARK)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7)
    ax.axis("off")
    for cx, cy, r, a in [(1,6,2,.07),(9,1,2.5,.05),(5,3.5,4,.04)]:
        ax.add_patch(plt.Circle((cx,cy), r, color=BLUE, alpha=a))
    ax.text(5, 5.2, "PromoFest", fontsize=42, fontweight="bold",
            color="white", ha="center")
    ax.text(5, 4.4, "Sistema de Confirmacion de Asistencia",
            fontsize=16, color="#93C5FD", ha="center")
    ax.plot([1.5,8.5],[3.9,3.9], color=BLUE, lw=1.5, alpha=0.4)
    ax.text(5, 3.3, "Diagramas de Flujo y Arquitectura",
            fontsize=12, color="#D1D5DB", ha="center")
    ax.text(5, 2.8, "Feria de Promociones 2025",
            fontsize=10, color="#9CA3AF", ha="center")
    items = [
        "1.  Flujo de Autenticacion (Registro e Inicio de Sesion)",
        "2.  Flujo de Confirmacion de Asistencia",
        "3.  Secuencia Backend — Transaccion y Control de Cupo",
        "4.  Mecanismo Anti-Overbooking (Concurrencia)",
        "5.  Patron Outbox — Notificaciones al Equipo de Ventas",
        "6.  Panel de Ventas — Flujo del Administrador",
    ]
    for i, item in enumerate(items):
        ax.text(5, 2.05-i*0.38, item, fontsize=9,
                color="#E5E7EB", ha="center")
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA 2 — Autenticacion (dos columnas)
# XW=14: 1 unidad = 0.609 in → BW=2.8 = 1.70 in (cabe ~24 chars @ 8.5pt)
# ══════════════════════════════════════════════════════════════════════════════

def page_auth(pdf):
    fig, ax = new_fig("1. Flujo de Autenticacion", "Registro e Inicio de Sesion")

    LX, RX = 3.5, 10.5   # centros columnas
    BW = 2.8              # ancho cajas principales
    DIV = 7.0             # divisor vertical

    ax.plot([DIV,DIV],[0.9,10.9], color="#D1D5DB", lw=1, ls="--", alpha=0.7)

    # ── REGISTRO (izquierda) ──────────────────────────────────────────────────
    ax.text(LX, 10.75, "REGISTRO", fontsize=9, fontweight="bold",
            color=BLUE, ha="center")
    terminal(ax, LX, YTOP, BW+0.4, "Usuario abre la app")
    arr(ax, LX, YTOP-0.47, LX, 9.5)

    box(ax, LX, 9.2, BW, 0.52, "Elige \"Crear cuenta\"")
    arr(ax, LX, 8.94, LX, 8.5)

    box(ax, LX, 8.2, BW, 0.55, "Ingresa email\n+ contrasena")
    arr(ax, LX, 7.92, LX, 7.5)

    box(ax, LX, 7.2, BW, 0.52, "POST /api/auth/register", color=PURPLE)
    arr(ax, LX, 6.94, LX, 6.4)

    diamond(ax, LX, 6.0, 2.8, 0.70, "Email ya\nregistrado?")
    # Si → error
    ax.text(LX+1.55, 6.2, "Si", fontsize=8, color=RED, fontweight="bold")
    arr(ax, LX+1.4, 6.0, LX+2.0, 6.0, color=RED)
    box(ax, LX+2.9, 6.0, 1.7, 0.68, "Error 409\nEmail en uso", color=RED, fontsize=8)
    # No ↓
    arr(ax, LX, 5.65, LX, 5.15, "No")

    box(ax, LX, 4.85, BW, 0.55, "Hash bcrypt\nCrea user, role='client'")
    arr(ax, LX, 4.57, LX, 4.1)

    box(ax, LX, 3.8, BW, 0.55, "Firma JWT\n(userId + email + role)", color=PURPLE)
    arr(ax, LX, 3.52, LX, 3.05)

    box(ax, LX, 2.75, BW, 0.52, "Guarda token\nen localStorage")
    arr(ax, LX, 2.49, LX, YBOT+0.47)

    terminal(ax, LX, YBOT, BW+0.4, "Redirige segun rol", color=GREEN)

    # ── LOGIN (derecha) ───────────────────────────────────────────────────────
    ax.text(RX, 10.75, "INICIO DE SESION", fontsize=9, fontweight="bold",
            color=ORANGE, ha="center")
    terminal(ax, RX, YTOP, BW+0.4, "Usuario tiene cuenta")
    arr(ax, RX, YTOP-0.47, RX, 9.5)

    box(ax, RX, 9.2, BW, 0.55, "Ingresa email\n+ contrasena")
    arr(ax, RX, 8.92, RX, 8.5)

    box(ax, RX, 8.2, BW, 0.52, "POST /api/auth/login", color=PURPLE)
    arr(ax, RX, 7.94, RX, 7.35)

    diamond(ax, RX, 6.95, 2.8, 0.70, "Credenciales\ncorrectas?")
    # No → error
    ax.text(RX+1.55, 7.15, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, RX+1.4, 6.95, RX+2.0, 6.95, color=RED)
    box(ax, RX+2.85, 6.95, 1.7, 0.78, "Error 401\nCredenciales\nincorrectas",
        color=RED, fontsize=7.5)
    # Si ↓
    arr(ax, RX, 6.60, RX, 6.05, "Si")

    box(ax, RX, 5.75, BW, 0.55, "Firma JWT\n(userId + email + role)", color=PURPLE)
    arr(ax, RX, 5.47, RX, 5.0)

    box(ax, RX, 4.7, BW, 0.52, "Guarda token\nen localStorage")
    arr(ax, RX, 4.44, RX, 3.9)

    diamond(ax, RX, 3.5, 2.6, 0.70, "role =\n'admin'?")
    # Si → /admin (derecha, dentro del xlim=14)
    ax.text(RX+1.4, 3.7, "Si", fontsize=8, color=ORANGE, fontweight="bold")
    arr(ax, RX+1.3, 3.5, RX+1.9, 3.5, color=ORANGE)
    box(ax, RX+2.85, 3.5, 1.9, 0.55,
        "Redirige a\n/admin", color=ORANGE, fontsize=8)
    # No ↓
    arr(ax, RX, 3.15, RX, 2.65, "No")
    box(ax, RX, 2.4, BW+0.4, 0.45,
        "Redirige a /confirm (ConfirmPage)", color=GREEN, fontsize=8)

    # Leyenda
    leg(ax, 0.35, BLUE,   "Proceso")
    leg(ax, 2.1,  AMBER,  "Decision")
    leg(ax, 3.9,  GREEN,  "Inicio / Fin")
    leg(ax, 5.6,  RED,    "Error")
    leg(ax, 7.2,  PURPLE, "API / DB")

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA 3 — Confirmacion (usuario)
# Columna principal: CX=5.5  Ramas derechas: x=9.5-12
# ══════════════════════════════════════════════════════════════════════════════

def page_confirm_user(pdf):
    fig, ax = new_fig("2. Flujo de Confirmacion de Asistencia",
                      "Perspectiva del usuario")

    CX = 5.5    # centro flujo principal
    BW = 4.5    # ancho cajas principales

    # — Inicio ———————————————————————————————————————————————————————————————
    terminal(ax, CX, YTOP, BW, "Usuario autenticado en /confirm")
    arr(ax, CX, YTOP-0.47, CX, 9.55)

    box(ax, CX, 9.3, BW, 0.65,
        "Carga inicial en paralelo:\nCatalogo · Evento · Confirmacion existente",
        color=PURPLE, fontsize=8)
    arr(ax, CX, 8.97, CX, 8.45)

    # — Decision: ya confirmo? ————————————————————————————————————————————————
    diamond(ax, CX, 8.08, 2.8, 0.68, "Ya confirmo\nanteriormente?")
    # Si → columna derecha alta (x=10.5), completamente separada del flujo
    ax.text(CX+1.5, 8.28, "Si", fontsize=8, color=AMBER, fontweight="bold")
    arr(ax, CX+1.4, 8.08, 9.2, 8.08, color=AMBER)
    box(ax, 10.5, 8.08, 2.8, 0.75,
        "Pantalla\nAlreadyConfirmed\n(resumen cupo)", color=AMBER, fontsize=8)
    arr(ax, 10.5, 7.70, 10.5, 7.25, color=AMBER)
    box(ax, 10.5, 7.0, 2.2, 0.45, "Cerrar sesion", color=GRAY, fontsize=8)
    # No ↓
    arr(ax, CX, 7.74, CX, 7.25, "No")

    # — Decision: evento lleno? ———————————————————————————————————————————————
    diamond(ax, CX, 6.88, 2.6, 0.65, "Evento lleno?")
    # Si → rama derecha baja (x=9.5, sin tocar la rama alta)
    ax.text(CX+1.4, 7.06, "Si", fontsize=8, color=RED, fontweight="bold")
    arr(ax, CX+1.3, 6.88, 8.95, 6.88, color=RED)
    box(ax, 10.3, 6.88, 2.6, 0.62,
        "Banner:\nCupo maximo alcanzado", color=RED, fontsize=8)
    # No ↓
    arr(ax, CX, 6.55, CX, 6.05, "No")

    # — Paso 1 ————————————————————————————————————————————————————————————————
    ax.text(1.5, 5.9, "PASO 1", fontsize=8.5, color=BLUE,
            fontweight="bold", ha="center")
    box(ax, CX, 5.72, BW, 0.62,
        "Nombre · Apellido · Email (bloqueado)\nSelecciona fecha/hora de sesion")
    arr(ax, CX, 5.41, CX, 4.88)

    diamond(ax, CX, 4.52, 2.6, 0.65, "Datos\nvalidos?")
    # No → curva de vuelta
    ax.text(CX+1.4, 4.7, "No", fontsize=8, color=RED, fontweight="bold")
    ax.annotate("", xy=(CX+BW/2, 5.72), xytext=(CX+1.3, 4.52),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.4,
                                connectionstyle="arc3,rad=-0.35"))
    note(ax, CX+3.8, 5.1, "Muestra errores\nde validacion", RED)
    # Si ↓
    arr(ax, CX, 4.19, CX, 3.7, "Si")

    # — Paso 2 ————————————————————————————————————————————————————————————————
    ax.text(1.5, 3.6, "PASO 2", fontsize=8.5, color=GREEN,
            fontweight="bold", ha="center")
    box(ax, CX, 3.38, BW, 0.55,
        "Seleccion servicios y productos\nDescuentos calculados en tiempo real")
    arr(ax, CX, 3.10, CX, 2.6)

    # — Decision: al menos 1 item? ————————————————————————————————————————————
    diamond(ax, CX, 2.22, 2.6, 0.65, "Al menos\n1 item?")
    # No → nota derecha
    ax.text(CX+1.4, 2.38, "No", fontsize=8, color=GRAY, fontweight="bold")
    arr(ax, CX+1.3, 2.22, CX+2.6, 2.22, color=GRAY)
    note(ax, CX+4.0, 2.22, "Boton Confirmar\ndisabled", GRAY)
    # Si ↓ → terminal
    arr(ax, CX, 1.89, CX, YBOT+0.47, "Si")

    terminal(ax, CX, YBOT, BW+1.0,
             "POST /api/attendees/confirm  ->  Ver diagrama 3",
             color=PURPLE, fontsize=8)

    # Leyenda
    leg(ax, 0.35, BLUE,   "Proceso")
    leg(ax, 2.1,  AMBER,  "Decision")
    leg(ax, 3.9,  GREEN,  "Exito / Inicio")
    leg(ax, 5.7,  RED,    "Error / Lleno")
    leg(ax, 7.5,  GRAY,   "Inactivo")

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA 4 — Secuencia Backend
# Actores: FX=1.5  EX=5.0  DBX=9.5  DSX=12.5  (dentro de xlim=14)
# ══════════════════════════════════════════════════════════════════════════════

def page_backend_sequence(pdf):
    fig, ax = new_fig("3. Secuencia Backend — Confirmacion",
                      "POST /api/attendees/confirm")

    FX, EX, DBX, DSX = 1.5, 5.0, 9.5, 12.5
    ACTORS = [(FX,"Frontend\n(React)",BLUE),(EX,"Express\nAPI",GREEN),
              (DBX,"PostgreSQL\n(DB)",PURPLE),(DSX,"Discount\nService",AMBER)]

    for x, name, c in ACTORS:
        box(ax, x, YTOP, 2.0, 0.52, name, color=c, fontsize=8)
        ax.plot([x,x],[0.5, YTOP-0.27], color=c, lw=1.2, ls="--", alpha=0.35)

    def msg(y, x1, x2, text, color=DARK, ret=False):
        style = "<-" if ret else "->"
        ax.annotate("", xy=(x2,y), xytext=(x1,y),
                    arrowprops=dict(arrowstyle=style, color=color, lw=1.5,
                                   connectionstyle="arc3,rad=0"))
        ax.text((x1+x2)/2, y+0.13, text, fontsize=7, color=color,
                ha="center", fontweight="bold" if not ret else "normal")

    def nseq(y, x, text, color=GRAY):
        ax.text(x, y, f"[ {text} ]", fontsize=6.8, color=color,
                ha="center", style="italic")

    y = YTOP - 0.55
    msg(y, FX, EX, "POST /confirm  {datos + item_ids}")
    y -= 0.30; nseq(y, EX, "Middleware: valida JWT", GREEN)
    y -= 0.26; nseq(y, EX, "Middleware: valida Zod schema", GREEN)
    y -= 0.33; msg(y, EX, DBX, "SELECT catalog_items WHERE id IN (...)")
    y -= 0.27; msg(y, DBX, EX, "items[ ]", ret=True, color=PURPLE)
    y -= 0.32; msg(y, EX, DBX, "SELECT attendees WHERE email = ?")
    y -= 0.27; msg(y, DBX, EX, "existing?", ret=True, color=PURPLE)
    y -= 0.26; nseq(y, DBX, "409 si ya existe confirmacion", RED)
    y -= 0.33; msg(y, EX, DSX, "calculateDiscounts(items)", color=AMBER)
    y -= 0.27; msg(y, DSX, EX, "{servicesDiscount, productsDiscount}", ret=True, color=AMBER)
    y -= 0.36

    tx_top = y + 0.15
    msg(y, EX, DBX, "BEGIN TRANSACTION", color=PURPLE)
    y -= 0.30; msg(y, EX, DBX, "SELECT event_config FOR UPDATE  <- BLOQUEO")
    y -= 0.27; msg(y, DBX, EX, "{capacity, confirmed_count}", ret=True, color=PURPLE)
    y -= 0.26; nseq(y, DBX, "409 si cupo agotado", RED)
    y -= 0.31; msg(y, EX, DBX, "INSERT INTO attendees (...)")
    y -= 0.27; msg(y, EX, DBX, "INSERT INTO attendee_items (...)")
    y -= 0.27; msg(y, EX, DBX, "UPDATE event_config SET confirmed_count + 1")
    y -= 0.31; msg(y, EX, DBX, "COMMIT  — libera el lock", color=GREEN)
    tx_bot = y - 0.1

    ax.add_patch(mpatches.FancyBboxPatch(
        (EX-0.9, tx_bot), DBX-EX+1.8, tx_top-tx_bot,
        boxstyle="round,pad=0.08", facecolor="none", edgecolor=PURPLE,
        linewidth=1.5, linestyle="--", zorder=2))
    ax.text(EX-0.85, (tx_top+tx_bot)/2, "Tx\nDB",
            fontsize=6.5, color=PURPLE, va="center", rotation=90)

    y -= 0.36; msg(y, EX, DBX, "SELECT attendee + items (respuesta completa)")
    y -= 0.27; msg(y, DBX, EX, "fullAttendee", ret=True, color=PURPLE)
    y -= 0.31; nseq(y, EX, "notifySalesTeam() — async, no bloquea", GRAY)
    y -= 0.27; msg(y, EX, FX, "201 {attendee, discounts, spots_remaining}",
                   ret=True, color=GREEN)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA 5 — Anti-Overbooking
# ══════════════════════════════════════════════════════════════════════════════

def page_overbooking(pdf):
    fig, ax = new_fig("4. Mecanismo Anti-Overbooking",
                      "Control de concurrencia con SELECT FOR UPDATE")

    T1X, DBX, T2X = 3.0, 7.0, 11.0

    for x, name, c in [(T1X,"Transaccion 1\n(Usuario A)",BLUE),
                        (DBX,"PostgreSQL\nevent_config (1 cupo)",PURPLE),
                        (T2X,"Transaccion 2\n(Usuario B)",ORANGE)]:
        box(ax, x, YTOP, 2.8, 0.52, name, color=c, fontsize=8)
        ax.plot([x,x],[1.6, YTOP-0.27], color=c, lw=1.2, ls="--", alpha=0.35)

    def smsg(y, x1, x2, text, color=DARK, dashed=False):
        ls = (0,(5,3)) if dashed else "-"
        ax.annotate("", xy=(x2,y), xytext=(x1,y),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5,
                                   connectionstyle="arc3,rad=0", linestyle=ls))
        ax.text((x1+x2)/2, y+0.14, text, fontsize=7.5, color=color,
                ha="center", fontweight="bold")

    def snote(y, x, text, color=DARK, bg=None):
        if bg:
            ax.add_patch(FancyBboxPatch((x-2.0, y-0.22), 4.0, 0.44,
                                        boxstyle="round,pad=0.05",
                                        facecolor=bg, edgecolor="none",
                                        alpha=0.22, zorder=2))
        ax.text(x, y, text, fontsize=7.5, color=color,
                ha="center", va="center", fontweight="bold")

    y = YTOP - 0.55
    smsg(y, T1X, DBX, "BEGIN TRANSACTION")
    y -= 0.30; smsg(y, T2X, DBX, "BEGIN TRANSACTION", color=ORANGE)
    y -= 0.46; smsg(y, T1X, DBX, "SELECT ... FOR UPDATE", color=BLUE)
    y -= 0.30; snote(y, DBX, "T1 ADQUIERE EL LOCK  [LOCKED]", BLUE, bg=BLUE)
    y -= 0.33; smsg(y, DBX, T1X, "spots_remaining = 1  [OK]", color=BLUE, dashed=True)
    y -= 0.40; smsg(y, T2X, DBX, "SELECT ... FOR UPDATE", color=ORANGE)
    y -= 0.30; snote(y, DBX, "T2 BLOQUEADA — espera a T1  [WAIT]", ORANGE, bg=ORANGE)
    y -= 0.48; smsg(y, T1X, DBX, "INSERT attendee (Usuario A)", color=BLUE)
    y -= 0.28; smsg(y, T1X, DBX, "UPDATE confirmed_count + 1", color=BLUE)
    y -= 0.28; smsg(y, T1X, DBX, "COMMIT  — libera lock", color=GREEN)
    snote(y-0.29, DBX, "Lock liberado  [UNLOCKED]", GREEN, bg=GREEN)
    y -= 0.66; snote(y, DBX, "T2 recibe el lock — lee nueva foto", ORANGE, bg=ORANGE)
    y -= 0.33; smsg(y, DBX, T2X, "spots_remaining = 0  [X]", color=RED, dashed=True)
    y -= 0.33; snote(y, T2X, "ROLLBACK", RED, bg=RED)
    y -= 0.30; ax.text(T2X, y, "Error 409: Evento lleno", fontsize=8.5,
                       color=RED, ha="center", fontweight="bold")
    y -= 0.42; ax.text(DBX, y,
                       "Resultado: Solo Usuario A confirmado — cupo nunca superado",
                       fontsize=9, color=GREEN, ha="center", fontweight="bold")

    note_box(ax, 0.85, 0.88,
             "SQL clave dentro de la transaccion:",
             "SELECT capacity, confirmed_count  FROM event_config  WHERE id = 1  FOR UPDATE;",
             bc=BLUE, fc="#EFF6FF")

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA 6 — Patron Outbox
# CX=6  BW=4.2  ramas derecha: x=11
# ══════════════════════════════════════════════════════════════════════════════

def page_outbox(pdf):
    fig, ax = new_fig("5. Patron Outbox — Notificaciones al Equipo de Ventas",
                      "Notificacion asincrona sin bloqueo")

    CX  = 6.0
    BW  = 4.2
    RBX = 11.0  # centro cajas error/retry

    terminal(ax, CX, YTOP, BW, "COMMIT exitoso — Asistente confirmado")
    arr(ax, CX, YTOP-0.47, CX, 9.55)

    box(ax, CX, 9.28, BW, 0.62,
        "notifySalesTeam(attendee, items)\n[async — no bloquea la respuesta]",
        color=GRAY)
    # Respuesta inmediata al cliente (rama derecha desde el bloque async)
    arr(ax, CX+BW/2, 9.28, RBX-1.1, 9.28, color=GREEN, lw=2.0)
    box(ax, RBX+0.9, 8.75, 2.4, 1.0,
        "201 al cliente\n\nConfirmacion\nno depende de\nla notificacion",
        color=GREEN, fontsize=7.5)
    ax.text(RBX-0.1, 9.5, "Respuesta\ninmediata",
            fontsize=7.5, color=GREEN, ha="center", fontweight="bold")

    arr(ax, CX, 8.97, CX, 8.4)

    box(ax, CX, 8.12, BW, 0.55,
        "INSERT notification_log\nstatus='pending', payload=snapshot completo",
        color=PURPLE, fontsize=8)
    arr(ax, CX, 7.84, CX, 7.3)

    box(ax, CX, 7.02, BW, 0.62,
        "simulateSend(payload)\nActual: logger.info (Winston)\nProd.: SendGrid / SQS / Twilio",
        color=BLUE, fontsize=8)
    arr(ax, CX, 6.71, CX, 6.15)

    diamond(ax, CX, 5.78, 2.8, 0.68, "Envio\nexitoso?")

    # Si ↓
    arr(ax, CX, 5.44, CX, 4.92, "Si")
    box(ax, CX, 4.62, BW, 0.55,
        "UPDATE notification_log\nstatus = 'sent',  sent_at = now()", color=GREEN)
    arr(ax, CX, 4.34, CX, 3.82)
    box(ax, CX, 3.52, BW, 0.52,
        "UPDATE attendees  SET notified_at = now()", color=GREEN)
    arr(ax, CX, 3.26, CX, YBOT+0.47)
    terminal(ax, CX, YBOT, BW,
             "Admin ve marca [OK] en columna Notif.", color=GREEN)

    # No → rama derecha
    ax.text(CX+1.5, 5.96, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, CX+1.4, 5.78, RBX-1.35, 5.78, color=RED)
    box(ax, RBX, 5.78, 2.9, 0.72,
        "UPDATE notification_log\nstatus = 'failed'\nlast_error = msg",
        color=RED, fontsize=8)
    arr(ax, RBX, 5.42, RBX, 4.85, color=RED)
    box(ax, RBX, 4.55, 2.9, 0.72,
        "Registro para retry\nmanual o job automatico\n(status='failed')",
        color=AMBER, fontsize=7.5)

    note_box(ax, 0.85, 0.82,
             "Migracion a produccion: reemplazar simulateSend() con llamada real",
             "SendGrid -> email  |  Twilio -> SMS/WhatsApp  |  AWS SQS -> cola async  |  Slack Webhook",
             bc=AMBER, fc="#FFF7ED")

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PAGINA 7 — Panel Admin
# ══════════════════════════════════════════════════════════════════════════════

def page_admin(pdf):
    fig, ax = new_fig("6. Panel de Ventas — Flujo del Administrador",
                      "Vista exclusiva role='admin'")

    CX = 7.0
    BW = 5.0

    terminal(ax, CX, YTOP, BW+1.0,
             "Admin hace login\nADMIN_EMAIL  /  ADMIN_PASSWORD")
    arr(ax, CX, YTOP-0.47, CX, 9.5)

    diamond(ax, CX, 9.1, 3.0, 0.70, "role === 'admin'?")
    # No →
    ax.text(CX+1.6, 9.3, "No", fontsize=8, color=RED, fontweight="bold")
    arr(ax, CX+1.5, 9.1, CX+2.2, 9.1, color=RED)
    box(ax, CX+3.5, 9.1, 2.6, 0.62,
        "AdminRoute redirige\na /confirm", color=RED, fontsize=8)
    # Si ↓
    arr(ax, CX, 8.75, CX, 8.2, "Si -> /admin")

    box(ax, CX, 7.9, BW, 0.55,
        "GET /api/attendees\n(Bearer token requerido, role=admin)", color=PURPLE)
    arr(ax, CX, 7.62, CX, 7.05)

    box(ax, CX, 6.75, BW, 0.62,
        "Responde: attendees[ ] + event\n{capacity, confirmed_count, spots_remaining}",
        color=PURPLE, fontsize=8)
    arr(ax, CX, 6.44, CX, 5.9)

    ax.text(CX, 5.72, "Dashboard — KPIs", fontsize=9, color=ORANGE,
            ha="center", fontweight="bold")
    kpis = [(2.5,5.2,"Confirmados\n/ Capacidad",BLUE),
            (5.3,5.2,"En filtro\nactual",GRAY),
            (8.1,5.2,"Servicios\ntotales",GREEN),
            (10.9,5.2,"Productos\ntotales",AMBER)]
    for x, y, label, c in kpis:
        box(ax, x, y, 2.2, 0.72, label, color=c, fontsize=8)
        arr(ax, x, 4.84, x, 4.42)

    ax.text(CX, 4.22, "Filtros client-side (sin nueva llamada al API)",
            fontsize=8.5, color=DARK, ha="center", fontweight="bold")

    box(ax, 4.0, 3.82, 3.2, 0.58, "Busqueda por\nnombre o email",
        color=BLUE, fontsize=8)
    box(ax, 10.0, 3.82, 3.2, 0.58, "Filtro por\nfecha de sesion",
        color=BLUE, fontsize=8)
    arr(ax, 4.0, 3.53, 4.0, 3.15)
    arr(ax, 10.0, 3.53, 10.0, 3.15)
    arr(ax, 4.0, 3.15, CX, 3.15)
    arr(ax, 10.0, 3.15, CX, 3.15)
    arr(ax, CX, 3.15, CX, 2.82)

    box(ax, CX, 2.52, 12.5, 0.52,
        "Tabla: Nombre · Email · Sesion · Servicios · Productos"
        " · Desc.Srv · Desc.Prod · Fecha · Notif.",
        color=ORANGE, fontsize=7.8)
    arr(ax, CX, 2.26, CX, YBOT+0.47)

    terminal(ax, CX, YBOT, BW,
             "Salir -> logout() -> localStorage limpiado", color=GRAY)

    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"Generando: {OUTPUT}")
    with PdfPages(OUTPUT) as pdf:
        d = pdf.infodict()
        d["Title"]   = "PromoFest — Diagramas de Flujo"
        d["Author"]  = "PromoFest / Feria de Promociones 2025"
        d["Subject"] = "Diagramas tecnicos del sistema de confirmacion"
        page_cover(pdf)
        page_auth(pdf)
        page_confirm_user(pdf)
        page_backend_sequence(pdf)
        page_overbooking(pdf)
        page_outbox(pdf)
        page_admin(pdf)
    print("[OK] 7 paginas generadas.")


if __name__ == "__main__":
    main()
