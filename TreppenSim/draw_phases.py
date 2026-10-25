"""
TreppenSchlepper — 2-D scale drawing of all 4 climbing phases.

All coordinates are in millimetres; 1 mm = 1 drawing unit.
The figure is saved to results/phases_drawing.png.

Usage:
    python draw_phases.py
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                    # noqa: E402
import matplotlib.patches as mpatches             # noqa: E402
import matplotlib.transforms as mtransforms       # noqa: E402
import numpy as np                                # noqa: E402

os.makedirs("results", exist_ok=True)

# ── Design dimensions (mm) ────────────────────────────────────────────────────

RISE   = 180   # stair rise height
TREAD  = 270   # stair tread depth
L_OS   = 250   # OuterShell length
H_OS   = 140   # OuterShell box height (visual; full device height with EC = 500)
L_IS   = 250   # SlidingInnerShell length
H_IS   = 80    # IS box height
H_FP   = 18    # FootPlate thickness
W_FP   = 250   # FootPlate width
H_EC_RETRACTED = 60   # EC height when retracted (inside OS+IS stack)
H_EC_EXTENDED  = RISE + H_EC_RETRACTED  # EC height when fully extended
W_EC   = 40    # EC width
H_HC      = 30   # HC height (visual bar thickness)
W_HC      = 180  # HC width when extended (= hc_stroke shown as bar)
W_HC_BODY = 120  # HC body length when contracted (rod retracted)
IS_INDENT = 14   # x-margin each side when drawing IS inside OS (exposes OS frame)
R_WHEEL = 35   # wheel radius (70 mm diameter)
AXLE_FRONT = 50   # front axle from OS front face
AXLE_REAR  = 200  # rear axle from OS front face
AXLE_ABOVE_OS = 0.8   # wheel axis height above OS lower edge, as fraction of R_WHEEL
_FLOOR_RISE = (1 - AXLE_ABOVE_OS) * R_WHEEL  # OS bottom above tread (7 mm clearance)

# Colours
C_OS      = "#4A90D9"   # blue  — OuterShell
C_IS      = "#7EC8A0"   # green — SlidingInnerShell
C_FP      = "#A0522D"   # brown — FootPlate
C_EC      = "#E8A838"   # amber — ElevatorCylinder
C_HC      = "#D05050"   # red   — HorizontalCylinder
C_WHEEL   = "#333333"   # dark  — wheels
C_PAYLOAD = "#C8D8F0"   # light blue — payload
C_STAIR   = "#CCCCCC"   # grey  — stair treads
C_ARROW   = "#222222"

ALPHA_FILL = 0.85
LW = 1.2


# ── Patch helpers ─────────────────────────────────────────────────────────────

def rect(ax, x, y, w, h, color, label=None, lw=LW, alpha=ALPHA_FILL,
         hatch=None, zorder=2):
    """Draw a filled rectangle with black edge."""
    r = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="square,pad=0",
        linewidth=lw, edgecolor="black",
        facecolor=color, alpha=alpha,
        hatch=hatch, zorder=zorder,
    )
    ax.add_patch(r)
    if label:
        ax.text(x + w / 2, y + h / 2, label,
                ha="center", va="center", fontsize=6.5,
                fontweight="bold", color="black", zorder=zorder + 1)
    return r


def wheel(ax, cx, cy, r=R_WHEEL, zorder=4):
    """Draw a wheel (filled circle)."""
    c = plt.Circle((cx, cy), r, color=C_WHEEL, zorder=zorder)
    ax.add_patch(c)
    # Hub
    hub = plt.Circle((cx, cy), r * 0.25, color="white", zorder=zorder + 1)
    ax.add_patch(hub)


def stair_step(ax, x_edge, z_lower, rise, tread, n=3):
    """Draw n stair steps starting at (x_edge, z_lower)."""
    for i in range(n):
        x0 = x_edge + i * tread
        z0 = z_lower + i * rise
        # riser (vertical face)
        ax.plot([x0, x0], [z0, z0 + rise],
                color="#888888", lw=1.5, zorder=1)
        # tread (horizontal surface) — extends to next riser
        ax.plot([x0, x0 + tread], [z0 + rise, z0 + rise],
                color="#888888", lw=1.5, zorder=1)
        # fill tread
        tread_patch = mpatches.FancyBboxPatch(
            (x0, z_lower - 30), tread, z0 + rise - z_lower + 30,
            boxstyle="square,pad=0", linewidth=0,
            facecolor=C_STAIR, alpha=0.35, zorder=0,
        )
        ax.add_patch(tread_patch)


def dim_arrow(ax, x0, y0, x1, y1, label, offset=(0, 8), fontsize=6):
    """Draw a dimension line with arrows and a label."""
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(
            arrowstyle="<->", color=C_ARROW, lw=0.8,
        ),
        zorder=5,
    )
    mx, my = (x0 + x1) / 2 + offset[0], (y0 + y1) / 2 + offset[1]
    ax.text(mx, my, label, ha="center", va="bottom",
            fontsize=fontsize, color=C_ARROW, zorder=5)


# ── Phase drawing functions ───────────────────────────────────────────────────

def draw_phase1(ax, ox=0, oz=0):
    """
    Phase 1 — Approach.
    Device on flat ground, approaching step.
    IS is inside OS (fully retracted); EC is retracted.
    OS (y-axis larger) encloses IS — they overlap in Z.
    """
    ax.set_title("Phase 1 — Approach", fontsize=9, fontweight="bold", pad=4)

    # Stair
    stair_step(ax, ox + L_OS + 20, oz, RISE, TREAD, n=2)

    # Ground line
    ax.axhline(oz, color="#888888", lw=1, xmin=0, xmax=1, zorder=0)

    ec_x = ox + L_OS / 2 - W_EC / 2

    # OS bottom is _FLOOR_RISE above ground (wheel clearance gap).
    # FP, IS, EC are all retracted inside OS.
    # Layout (bottom to top inside OS): FP | IS | EC | (upper OS space) | payload
    os_z = oz + _FLOOR_RISE      # OS bottom 7 mm above ground
    is_z = os_z                  # IS at OS floor (inside OS)
    fp_z = os_z                  # FP at OS floor (retracted, inside OS)
    ec_z = fp_z + H_FP           # EC from FP top, inside IS

    # FootPlate retracted inside OS (same x-indent as IS so OS frame remains visible)
    rect(ax, ox + IS_INDENT, fp_z, W_FP - 2 * IS_INDENT, H_FP, C_FP, "FP", alpha=0.80)

    # OS drawn first; IS overlays it but IS is indented, exposing OS frame
    rect(ax, ox, os_z, L_OS, H_OS, C_OS, label=None)
    # OS label in the upper-right blue strip (above IS)
    ax.text(ox + L_OS - IS_INDENT / 2 - 2, os_z + H_IS + H_EC_RETRACTED * 0.55,
            "OS", ha="right", va="center", fontsize=6.5,
            fontweight="bold", color="black", zorder=3)

    # IS inside OS, indented in x so OS frame is visible on both sides
    rect(ax, ox + IS_INDENT, is_z, L_IS - 2 * IS_INDENT, H_IS, C_IS, "IS", alpha=0.80)

    # HC contracted: body at OS rear face (IS attachment = IS/OS rear = ox)
    hc_y = is_z + H_IS + (H_OS - H_IS - H_HC) / 2
    rect(ax, ox + IS_INDENT, is_z + H_IS, IS_INDENT, hc_y - (is_z + H_IS), C_HC, None, alpha=0.75, lw=0.8)
    rect(ax, ox, hc_y, W_HC_BODY, H_HC, C_HC, "HC", alpha=0.65)

    # EC retracted: from FP top upward, inside IS — drawn after IS so visible
    rect(ax, ec_x, ec_z, W_EC, H_EC_RETRACTED, C_EC, "EC", alpha=0.85)

    # Payload on OS
    rect(ax, ox + 20, os_z + H_OS, L_OS - 40, 60, C_PAYLOAD, "payload",
         alpha=0.5)

    # Wheels touch ground; axles mounted on OS sides
    wheel(ax, ox + AXLE_FRONT, oz + R_WHEEL)
    wheel(ax, ox + AXLE_REAR,  oz + R_WHEEL)

    # Motion arrow
    ax.annotate("", xy=(ox + L_OS + 18, oz + 60),
                xytext=(ox + L_OS - 20, oz + 60),
                arrowprops=dict(arrowstyle="->", color="#1155CC", lw=1.5),
                zorder=5)
    ax.text(ox + L_OS + 10, oz + 70, "drive", fontsize=6, color="#1155CC",
            ha="center")

    _axis_setup(ax, ox, oz)


def draw_phase2(ax, ox=0, oz=0):
    """
    Phase 2 — Elevation.
    EC (between FP and IS ceiling) extends, lifting IS+OS together. FP stays.
    """
    ax.set_title("Phase 2 — Elevation (EC extends)", fontsize=9,
                 fontweight="bold", pad=4)

    stair_step(ax, ox + L_IS + 10, oz, RISE, TREAD, n=2)


    # FP stays on lower tread
    fp_z = oz
    rect(ax, ox, fp_z, W_FP, H_FP, C_FP, "FP")

    ec_x = ox + L_OS / 2 - W_EC / 2
    ec_z_bottom = fp_z + H_FP

    # IS+OS elevated; OS bottom = upper tread + clearance gap
    upper_z = oz + RISE
    os_z = upper_z + _FLOOR_RISE  # = RISE + 7 mm clearance
    is_z = os_z                    # IS at OS floor
    is_top = is_z + H_IS
    ec_height = is_top - ec_z_bottom  # EC spans FP top → IS ceiling

    # OS (enclosing IS) — drawn first as background
    rect(ax, ox, os_z, L_OS, H_OS, C_OS, label=None)
    ax.text(ox + L_OS - IS_INDENT / 2 - 2, os_z + H_IS + H_EC_RETRACTED * 0.55,
            "OS", ha="right", va="center", fontsize=6.5,
            fontweight="bold", color="black", zorder=3)
    rect(ax, ox + 20, os_z + H_OS, L_OS - 40, 60, C_PAYLOAD, "payload",
         alpha=0.5)

    # IS inside OS, indented to expose OS frame
    rect(ax, ox + IS_INDENT, is_z, L_IS - 2 * IS_INDENT, H_IS, C_IS, "IS")

    # HC contracted: body at OS rear face (IS attachment = IS/OS rear = ox)
    hc_y = is_top + (H_OS - H_IS - H_HC) / 2
    rect(ax, ox + IS_INDENT, is_top, IS_INDENT, hc_y - is_top, C_HC, None, alpha=0.75, lw=0.8)
    rect(ax, ox, hc_y, W_HC_BODY, H_HC, C_HC, "HC", alpha=0.65)

    # EC drawn after IS so it is visible from FP all the way to IS ceiling
    rect(ax, ec_x, ec_z_bottom, W_EC, ec_height, C_EC, "EC↑")

    # Wheels on upper tread (device elevated to upper-tread height)
    wheel(ax, ox + AXLE_FRONT, upper_z + R_WHEEL)
    wheel(ax, ox + AXLE_REAR,  upper_z + R_WHEEL)

    # Dimension arrow: rise height (EC extension = RISE)
    dim_arrow(ax, ox - 25, ec_z_bottom,
              ox - 25, ec_z_bottom + RISE,
              f"{RISE} mm", offset=(-35, 0))

    # EC upward motion arrow
    ax.annotate("", xy=(ec_x - 15, ec_z_bottom + H_EC_EXTENDED * 0.8),
                xytext=(ec_x - 15, ec_z_bottom + H_EC_EXTENDED * 0.3),
                arrowprops=dict(arrowstyle="->", color="#CC6600", lw=1.5),
                zorder=5)

    _axis_setup(ax, ox, oz)


def draw_phase3(ax, ox=0, oz=0):
    """
    Phase 3 — HC Advance.
    EC still extended, holding IS (+ FP below) at upper height.
    HC pushes OS forward 250 mm; IS stays at original x.
    """
    ax.set_title("Phase 3 — HC Advance (OS slides forward)", fontsize=9,
                 fontweight="bold", pad=4)

    hc_stroke = 250   # mm — end of phase

    stair_step(ax, ox + L_IS + 10, oz, RISE, TREAD, n=2)

    # FP still on lower tread
    fp_z = oz
    rect(ax, ox, fp_z, W_FP, H_FP, C_FP, "FP")

    ec_x = ox + L_OS / 2 - W_EC / 2
    ec_z_bottom = fp_z + H_FP

    # IS still elevated (same height as Phase 2 end); OS same level
    upper_tread_z = oz + RISE
    is_z = upper_tread_z + _FLOOR_RISE   # IS bottom = upper tread + clearance
    os_z = is_z
    is_top = is_z + H_IS
    ec_height = is_top - ec_z_bottom     # EC spans FP top → IS ceiling

    # EC still fully extended (holds IS at elevated position)
    rect(ax, ec_x, ec_z_bottom, W_EC, ec_height, C_EC, "EC")

    # hc_y needed for bracket height — compute before IS drawing
    hc_y = is_top + (H_OS - H_IS - H_HC) / 2

    # IS elevated at original x; indented like other phases for visual consistency
    rect(ax, ox + IS_INDENT, is_z, L_IS - 2 * IS_INDENT, H_IS, C_IS, "IS")

    # IS-HC connection bracket: vertical fixture at IS left face (rod attachment)
    rect(ax, ox + IS_INDENT, is_top, IS_INDENT, hc_y - is_top, C_HC, None, alpha=0.75, lw=0.8)

    # OS advanced by HC stroke
    os_x = ox + hc_stroke
    rect(ax, os_x, os_z, L_OS, H_OS, C_OS, "OS")
    rect(ax, os_x + 20, os_z + H_OS, L_OS - 40, 60, C_PAYLOAD, "payload",
         alpha=0.5)

    # HC extended: rod from IS rear (ox) to OS rear (os_x), body inside OS
    rect(ax, ox, hc_y, hc_stroke + W_HC_BODY, H_HC, C_HC, "HC→", alpha=0.65)

    # Wheels on upper tread (OS fully advanced)
    front_wheel_x = os_x + AXLE_FRONT
    rear_wheel_x  = os_x + AXLE_REAR
    wheel(ax, front_wheel_x, upper_tread_z + R_WHEEL)
    wheel(ax, rear_wheel_x,  upper_tread_z + R_WHEEL)

    # HC motion arrow (aligned with HC bar)
    ax.annotate("", xy=(os_x - 5, hc_y + H_HC / 2),
                xytext=(os_x - 45, hc_y + H_HC / 2),
                arrowprops=dict(arrowstyle="->", color="#CC2222", lw=1.5),
                zorder=5)

    _axis_setup(ax, ox, oz)


def draw_phase4(ax, ox=0, oz=0):
    """
    Phase 4 — Retract.
    HC retracts, pulling IS+FP back into OS.
    EC retracts to lower IS to OS floor level.
    Device fully on upper tread.
    """
    ax.set_title("Phase 4 — Retract (IS+FP pulled into OS)", fontsize=9,
                 fontweight="bold", pad=4)

    hc_stroke = 250

    # Stair at same position as Phase 3 (step edge at ox + L_IS + 10)
    stair_step(ax, ox + L_IS + 10, oz, RISE, TREAD, n=2)

    # OS fully on upper tread; IS+FP retracted INSIDE OS (mirrors Phase 1).
    # OS bottom = upper tread + clearance gap; FP at OS floor (inside OS).
    os_x = ox + hc_stroke  # where it ended up after Phase 3
    upper_z = oz + RISE

    os_z = upper_z + _FLOOR_RISE  # OS bottom 7 mm above upper tread
    is_z = os_z                    # IS at OS floor (inside OS)
    fp_z = os_z                    # FP retracted inside OS at OS floor
    ec_z = fp_z + H_FP             # EC from FP top, inside IS
    ec_x = os_x + L_OS / 2 - W_EC / 2

    # FP retracted inside OS (indented like IS so OS frame stays visible)
    rect(ax, os_x + IS_INDENT, fp_z, W_FP - 2 * IS_INDENT, H_FP, C_FP, "FP",
         alpha=0.70, lw=0.8)

    # OS (encloses IS in y-axis); drawn first
    rect(ax, os_x, os_z, L_OS, H_OS, C_OS, label=None)
    ax.text(os_x + L_OS - IS_INDENT / 2 - 2,
            os_z + H_IS + H_EC_RETRACTED * 0.55,
            "OS", ha="right", va="center", fontsize=6.5,
            fontweight="bold", color="black", zorder=3)
    rect(ax, os_x + 20, os_z + H_OS, L_OS - 40, 60, C_PAYLOAD, "payload",
         alpha=0.5)

    # IS inside OS, indented to expose OS frame
    rect(ax, os_x + IS_INDENT, is_z, L_IS - 2 * IS_INDENT, H_IS, C_IS,
         "IS (retracted)", alpha=0.80, lw=0.8)

    # HC contracted: body at OS rear face (IS attachment = IS/OS rear = os_x)
    hc_y = is_z + H_IS + (H_OS - H_IS - H_HC) / 2
    rect(ax, os_x + IS_INDENT, is_z + H_IS, IS_INDENT, hc_y - (is_z + H_IS), C_HC, None, alpha=0.75, lw=0.8)
    rect(ax, os_x, hc_y, W_HC_BODY, H_HC, C_HC, "HC←", alpha=0.65)

    # EC retracted: from FP top upward inside IS — drawn after IS so visible
    rect(ax, ec_x, ec_z, W_EC, H_EC_RETRACTED, C_EC, "EC↓", alpha=0.85)

    # Wheels — both on upper tread
    wheel(ax, os_x + AXLE_FRONT, upper_z + R_WHEEL)
    wheel(ax, os_x + AXLE_REAR,  upper_z + R_WHEEL)

    # "Ready for next step" label
    ax.text(os_x + L_OS / 2, upper_z - 25, "ready for next step",
            ha="center", va="top", fontsize=6.5, style="italic",
            color="#226622")

    _axis_setup(ax, ox, oz)


def _axis_setup(ax, ox, oz):
    """Common axis formatting for a phase panel."""
    margin_x = 80
    margin_z = 60
    ax.set_xlim(ox - margin_x, ox + L_OS + TREAD + margin_x + 80)
    ax.set_ylim(oz - margin_z, oz + RISE + H_OS + 120)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)", fontsize=7)
    ax.set_ylabel("z (mm)", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, alpha=0.2, lw=0.5)

    # Axis origin marker
    ax.axhline(oz, color="#AAAAAA", lw=0.6, ls="--", zorder=0)
    ax.axvline(ox, color="#AAAAAA", lw=0.6, ls="--", zorder=0)


# ── Legend ────────────────────────────────────────────────────────────────────

def make_legend_patches():
    items = [
        (C_OS,      "OuterShell (OS)"),
        (C_IS,      "SlidingInnerShell (IS)"),
        (C_FP,      "FootPlate (FP)"),
        (C_EC,      "ElevatorCylinder (EC)"),
        (C_HC,      "HorizontalCylinder (HC)"),
        (C_WHEEL,   "Wheel (Ø 70 mm)"),
        (C_PAYLOAD, "Payload"),
        (C_STAIR,   "Stair"),
    ]
    return [mpatches.Patch(facecolor=c, edgecolor="black",
                           linewidth=0.8, label=l)
            for c, l in items]


# ── Main figure ───────────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(
    "TreppenSchlepper — 4 Climbing Phases (2-D side view, to scale)\n"
    "18/27 stair  |  OS=250×140 mm  |  IS=250×80 mm  |  "
    "Rise=180 mm  |  Tread=270 mm  |  Wheels Ø70 mm",
    fontsize=11, fontweight="bold",
)

draw_phase1(axes[0, 0])
draw_phase2(axes[0, 1])
draw_phase3(axes[1, 0])
draw_phase4(axes[1, 1])

fig.legend(
    handles=make_legend_patches(),
    loc="lower center", ncol=8, fontsize=7.5,
    frameon=True, edgecolor="gray",
    bbox_to_anchor=(0.5, 0.01),
)

plt.tight_layout(rect=[0, 0.05, 1, 0.95])

out = os.path.join("results", "phases_drawing.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Drawing saved -> {out}")
