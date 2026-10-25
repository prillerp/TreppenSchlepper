"""
TreppenSchlepper — 3-D scale drawing of all 4 climbing phases.

One 2×2 figure, each panel an isometric 3-D view of one phase.
All coordinates in millimetres; 1 drawing unit = 1 mm.

Usage:
    uv run python draw_3d.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                       # noqa: E402
import matplotlib.patches as mpatches                # noqa: E402
import numpy as np                                    # noqa: E402
from mpl_toolkits.mplot3d import Axes3D               # noqa: E402, F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

os.makedirs("results", exist_ok=True)

# ── Design dimensions (mm) — must match draw_phases.py ───────────────────────

RISE   = 180
TREAD  = 270
L_OS   = 250
H_OS   = 140
L_IS   = 250
H_IS   = 80
H_FP   = 18
W_FP   = 250
H_EC_RETRACTED = 60
H_EC_EXTENDED  = RISE + H_EC_RETRACTED
W_EC   = 40
H_HC   = 30
W_HC_BODY = 120
IS_INDENT = 14
R_WHEEL   = 35
AXLE_FRONT = 50
AXLE_REAR  = 200
AXLE_ABOVE_OS = 0.8
_FLOOR_RISE = (1 - AXLE_ABOVE_OS) * R_WHEEL   # 7 mm OS-bottom above tread

# ── 3-D dimensions (mm) — new in this file ────────────────────────────────────

W_OS          = 400    # OuterShell width (y-axis)
W_IS          = 370    # IS width (slightly narrower)
W_FP_Y        = 400    # FootPlate width (= W_OS)
W_EC_Y        = 40     # EC square cross-section
W_HC_Y        = 40     # HC square cross-section
W_WHEEL       = 50     # tyre width
WHEEL_TRACK   = 340    # centre-to-centre lateral distance
W_STAIR       = 1000   # stair clear width
H_PAYLOAD     = 60     # payload box height above OS top
PAYLOAD_INSET = 20     # payload box inset from OS sides

# ── Colours (same as draw_phases.py) ─────────────────────────────────────────

C_OS      = "#4A90D9"
C_IS      = "#7EC8A0"
C_FP      = "#A0522D"
C_EC      = "#E8A838"
C_HC      = "#D05050"
C_WHEEL   = "#333333"
C_PAYLOAD = "#C8D8F0"
C_STAIR   = "#CCCCCC"

AZ  = -130   # azimuth  (degrees) — default viewing angle
EL  =  30    # elevation (degrees)


# ── 3-D primitive helpers ─────────────────────────────────────────────────────

def _faces(x, y, z, dx, dy, dz):
    """Return the 6 faces of an axis-aligned box as lists of 4 vertices."""
    x1, y1, z1 = x + dx, y + dy, z + dz
    return [
        [(x, y, z), (x1, y, z), (x1, y1, z),  (x,  y1, z) ],   # bottom
        [(x, y, z1),(x1, y, z1),(x1, y1, z1), (x,  y1, z1)],   # top
        [(x, y, z), (x1, y, z), (x1, y, z1),  (x,  y, z1) ],   # front  (y-min)
        [(x, y1, z),(x1, y1, z),(x1, y1, z1), (x,  y1, z1)],   # back   (y-max)
        [(x, y, z), (x, y1, z), (x, y1, z1),  (x,  y, z1) ],   # left   (x-min)
        [(x1, y, z),(x1, y1, z),(x1, y1, z1), (x1, y, z1) ],   # right  (x-max)
    ]


def box3d(ax, x, y, z, dx, dy, dz, color, alpha=0.55, lw=0.4, zorder=2):
    """Draw a solid box with semi-transparent faces and dark edges."""
    poly = Poly3DCollection(
        _faces(x, y, z, dx, dy, dz),
        alpha=alpha, linewidth=lw, edgecolor="#111111",
        zsort="average", zorder=zorder,
    )
    poly.set_facecolor(color)
    ax.add_collection3d(poly)


def cylinder3d(ax, cx, cz, cy_min, cy_max, r, color, alpha=0.75, n=20):
    """Draw a cylinder with axis along y (used for wheels)."""
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    xs = cx + r * np.cos(theta)
    zs = cz + r * np.sin(theta)

    # Two end caps
    for cy in (cy_min, cy_max):
        verts = list(zip(xs, np.full(n, cy), zs))
        poly = Poly3DCollection([verts], alpha=alpha, linewidth=0.3,
                                edgecolor="#111111", zsort="average")
        poly.set_facecolor(color)
        ax.add_collection3d(poly)

    # Cylindrical wall as quads
    wall = []
    for i in range(n):
        j = (i + 1) % n
        wall.append([
            (xs[i], cy_min, zs[i]),
            (xs[j], cy_min, zs[j]),
            (xs[j], cy_max, zs[j]),
            (xs[i], cy_max, zs[i]),
        ])
    poly = Poly3DCollection(wall, alpha=alpha, linewidth=0.2,
                            edgecolor="none", zsort="average")
    poly.set_facecolor(color)
    ax.add_collection3d(poly)


def wheel3d(ax, cx, cz, cy_centre):
    """Draw one wheel (tyre + white hub) centred at (cx, cy_centre, cz)."""
    half = W_WHEEL / 2
    cylinder3d(ax, cx, cz, cy_centre - half, cy_centre + half,
               R_WHEEL, C_WHEEL, alpha=0.90)
    cylinder3d(ax, cx, cz, cy_centre - half - 1, cy_centre + half + 1,
               R_WHEEL * 0.28, "white", alpha=1.0, n=16)


def axle3d(ax, cx, cz, y_left, y_right):
    """Draw the wheel axle as a thin box."""
    r = 6   # axle half-height (mm)
    box3d(ax, cx - r, y_left, cz - r, 2 * r, y_right - y_left, 2 * r,
          "#555555", alpha=0.90, lw=0.2)


def stair3d(ax, x_edge, oz, n=3):
    """Draw n stair steps starting at x_edge on the y-symmetric centreline."""
    yw = W_STAIR / 2
    for i in range(n):
        x0 = x_edge + i * TREAD
        z0 = oz + i * RISE
        # tread surface
        box3d(ax, x0, -yw, oz - 30, TREAD, W_STAIR, z0 + RISE - oz + 30,
              C_STAIR, alpha=0.20, lw=0.3)


def ground3d(ax, x0, ox, oz):
    """Draw the lower tread surface."""
    yw = W_STAIR / 2
    box3d(ax, x0, -yw, oz - 8, ox - x0, W_STAIR, 8,
          C_STAIR, alpha=0.20, lw=0.2)


def _axis_setup(ax, ox, oz, title):
    """Common 3-D axis formatting."""
    ax.set_title(title, fontsize=9, fontweight="bold", pad=6)
    ax.set_xlabel("x (mm)", fontsize=7, labelpad=2)
    ax.set_ylabel("y (mm)", fontsize=7, labelpad=2)
    ax.set_zlabel("z (mm)", fontsize=7, labelpad=2)
    ax.tick_params(labelsize=6)
    ax.view_init(elev=EL, azim=AZ)

    margin_x = 80
    ax.set_xlim(ox - margin_x, ox + L_OS + TREAD + margin_x + 80)
    ax.set_ylim(-W_STAIR / 2 - 20, W_STAIR / 2 + 20)
    ax.set_zlim(oz - 20, oz + RISE + H_OS + H_PAYLOAD + 30)

    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor("lightgray")
    ax.yaxis.pane.set_edgecolor("lightgray")
    ax.zaxis.pane.set_edgecolor("lightgray")
    ax.grid(True, alpha=0.15)


# ── Reusable device-part drawing ──────────────────────────────────────────────

def _ec_box(ax, fp_x, fp_z, is_z):
    """
    Draw ElevatorCylinder anchored at the centre of FP (bottom) and
    centre of IS ceiling (top).

    Centre of FP  : x = fp_x + W_FP/2,  y = 0  (FP is y-symmetric about 0)
    Centre of IS ceiling: same x (W_FP = L_IS), same y = 0
    Bottom z: top surface of FP  = fp_z + H_FP
    Top    z: ceiling of IS      = is_z + H_IS
    """
    ec_x   = fp_x + W_FP / 2 - W_EC / 2   # centred in FP/IS along x
    ec_y   = -W_EC_Y / 2                   # centred in FP/IS along y (y=0 centre)
    ec_z0  = fp_z + H_FP                   # bottom: FP top surface
    ec_z1  = is_z + H_IS                   # top:    IS ceiling
    ec_h   = ec_z1 - ec_z0
    box3d(ax, ec_x, ec_y, ec_z0, W_EC, W_EC_Y, ec_h, C_EC, alpha=0.90)

    # Wireframe edges drawn as Line3D — always visible regardless of depth sort.
    # matplotlib Poly3DCollection sorting can hide filled boxes inside other boxes;
    # ax.plot lines always render on top and make EC unambiguously visible.
    x0, x1 = ec_x, ec_x + W_EC
    y0, y1 = ec_y, ec_y + W_EC_Y
    z0, z1 = ec_z0, ec_z1
    for xs, ys, zs in [
        # 4 vertical edges
        ([x0, x0], [y0, y0], [z0, z1]),
        ([x1, x1], [y0, y0], [z0, z1]),
        ([x0, x0], [y1, y1], [z0, z1]),
        ([x1, x1], [y1, y1], [z0, z1]),
        # 4 top edges
        ([x0, x1], [y0, y0], [z1, z1]),
        ([x1, x1], [y0, y1], [z1, z1]),
        ([x1, x0], [y1, y1], [z1, z1]),
        ([x0, x0], [y1, y0], [z1, z1]),
        # 4 bottom edges
        ([x0, x1], [y0, y0], [z0, z0]),
        ([x1, x1], [y0, y1], [z0, z0]),
        ([x1, x0], [y1, y1], [z0, z0]),
        ([x0, x0], [y1, y0], [z0, z0]),
    ]:
        ax.plot(xs, ys, zs, color=C_EC, lw=2.0, alpha=1.0)


def _draw_device(ax, os_x, os_z, is_x, is_z, fp_x, fp_z,
                 hc_x_left, hc_x_right,
                 draw_fp=True):
    """Draw OS, IS, FP, HC and payload.  EC is drawn separately via _ec_box."""
    oy_os = -W_OS / 2
    oy_is = -W_IS / 2
    oy_fp = -W_FP_Y / 2

    # FootPlate
    if draw_fp:
        box3d(ax, fp_x + IS_INDENT, oy_fp + IS_INDENT, fp_z,
              W_FP - 2 * IS_INDENT, W_FP_Y - 2 * IS_INDENT, H_FP,
              C_FP, alpha=0.80)

    # OuterShell (semi-transparent so IS/EC visible inside)
    box3d(ax, os_x, oy_os, os_z, L_OS, W_OS, H_OS, C_OS, alpha=0.35)

    # IS inside OS (slightly narrower, indented in x)
    box3d(ax, is_x + IS_INDENT, oy_is, is_z,
          L_IS - 2 * IS_INDENT, W_IS, H_IS, C_IS, alpha=0.55)

    # HorizontalCylinder bar (centred in y, in the IS/OS ceiling gap)
    hc_z = is_z + H_IS + (H_OS - H_IS - H_HC) / 2
    box3d(ax, hc_x_left, -W_HC_Y / 2, hc_z,
          hc_x_right - hc_x_left, W_HC_Y, H_HC, C_HC, alpha=0.80)

    # Payload box on top of OS
    px_inset = PAYLOAD_INSET
    box3d(ax, os_x + px_inset, oy_os + px_inset, os_z + H_OS,
          L_OS - 2 * px_inset, W_OS - 2 * px_inset, H_PAYLOAD,
          C_PAYLOAD, alpha=0.45)


def _draw_wheels(ax, os_x, oz_tread):
    """Draw 4 wheels + 2 axles on the OS."""
    cz = oz_tread + R_WHEEL
    y_left  = -WHEEL_TRACK / 2 - W_WHEEL / 2
    y_right =  WHEEL_TRACK / 2 + W_WHEEL / 2
    yc_l    = -WHEEL_TRACK / 2
    yc_r    =  WHEEL_TRACK / 2

    for axle_x in (os_x + AXLE_FRONT, os_x + AXLE_REAR):
        wheel3d(ax, axle_x, cz, yc_l)
        wheel3d(ax, axle_x, cz, yc_r)
        axle3d(ax, axle_x, cz, y_left, y_right)


# ── Shared stair environment (identical in all phases) ───────────────────────

def _draw_environment(ax, ox, oz):
    """Stair + lower ground — drawn identically in every phase."""
    stair3d(ax, ox + L_OS, oz, n=2)
    ground3d(ax, ox - 60, ox + L_OS, oz)


# ── Phase drawing functions ───────────────────────────────────────────────────

def draw_phase1_3d(ax, ox=0, oz=0):
    ax.set_title("Phase 1 — Approach", fontsize=9, fontweight="bold", pad=6)
    _draw_environment(ax, ox, oz)

    os_z = oz + _FLOOR_RISE
    is_z = os_z
    fp_z = os_z
    hc_left  = ox
    hc_right = ox + W_HC_BODY

    _draw_device(ax, ox, os_z, ox, is_z, ox, fp_z, hc_left, hc_right)
    _ec_box(ax, fp_x=ox, fp_z=fp_z, is_z=is_z)
    _draw_wheels(ax, ox, oz)
    _axis_setup(ax, ox, oz, "Phase 1 — Approach")


def draw_phase2_3d(ax, ox=0, oz=0):
    ax.set_title("Phase 2 — Elevation", fontsize=9, fontweight="bold", pad=6)
    _draw_environment(ax, ox, oz)

    upper_z = oz + RISE
    os_z = upper_z + _FLOOR_RISE
    is_z = os_z
    fp_z = oz          # FP stays on lower tread
    hc_left  = ox
    hc_right = ox + W_HC_BODY

    # FP stays on lower tread — draw separately
    box3d(ax, ox + IS_INDENT, -W_FP_Y / 2 + IS_INDENT, fp_z,
          W_FP - 2 * IS_INDENT, W_FP_Y - 2 * IS_INDENT, H_FP,
          C_FP, alpha=0.80)

    _draw_device(ax, ox, os_z, ox, is_z, ox, fp_z, hc_left, hc_right, draw_fp=False)
    _ec_box(ax, fp_x=ox, fp_z=fp_z, is_z=is_z)
    _draw_wheels(ax, ox, upper_z)
    _axis_setup(ax, ox, oz, "Phase 2 — Elevation (EC extends)")


def draw_phase3_3d(ax, ox=0, oz=0):
    ax.set_title("Phase 3 — HC Advance", fontsize=9, fontweight="bold", pad=6)
    hc_stroke = 250
    _draw_environment(ax, ox, oz)

    upper_z = oz + RISE
    is_z    = upper_z + _FLOOR_RISE
    os_z    = is_z
    fp_z    = oz
    os_x    = ox + hc_stroke

    hc_left  = ox
    hc_right = os_x + W_HC_BODY

    # FP on lower tread
    box3d(ax, ox + IS_INDENT, -W_FP_Y / 2 + IS_INDENT, fp_z,
          W_FP - 2 * IS_INDENT, W_FP_Y - 2 * IS_INDENT, H_FP,
          C_FP, alpha=0.80)

    # IS stayed at ox (elevated)
    box3d(ax, ox + IS_INDENT, -W_IS / 2, is_z,
          L_IS - 2 * IS_INDENT, W_IS, H_IS, C_IS, alpha=0.75)

    # EC: centre of FP (bottom) → centre of IS ceiling (top)
    _ec_box(ax, fp_x=ox, fp_z=fp_z, is_z=is_z)

    # OS (advanced)
    box3d(ax, os_x, -W_OS / 2, os_z, L_OS, W_OS, H_OS, C_OS, alpha=0.35)

    # HC bar
    hc_z = is_z + H_IS + (H_OS - H_IS - H_HC) / 2
    box3d(ax, hc_left, -W_HC_Y / 2, hc_z,
          hc_right - hc_left, W_HC_Y, H_HC, C_HC, alpha=0.80)

    # Payload on OS
    box3d(ax, os_x + PAYLOAD_INSET, -W_OS / 2 + PAYLOAD_INSET, os_z + H_OS,
          L_OS - 2 * PAYLOAD_INSET, W_OS - 2 * PAYLOAD_INSET, H_PAYLOAD,
          C_PAYLOAD, alpha=0.45)

    _draw_wheels(ax, os_x, upper_z)
    _axis_setup(ax, ox, oz, "Phase 3 — HC Advance (OS slides forward)")


def draw_phase4_3d(ax, ox=0, oz=0):
    ax.set_title("Phase 4 — Retract", fontsize=9, fontweight="bold", pad=6)
    hc_stroke = 250

    upper_z = oz + RISE
    os_x    = ox + hc_stroke
    os_z    = upper_z + _FLOOR_RISE
    is_z    = os_z
    fp_z    = os_z
    hc_left  = os_x
    hc_right = os_x + W_HC_BODY

    _draw_environment(ax, ox, oz)

    _draw_device(ax, os_x, os_z, os_x, is_z, os_x, fp_z, hc_left, hc_right)
    _ec_box(ax, fp_x=os_x, fp_z=fp_z, is_z=is_z)
    _draw_wheels(ax, os_x, upper_z)
    _axis_setup(ax, ox, oz, "Phase 4 — Retract (IS+FP pulled back)")


# ── Legend ────────────────────────────────────────────────────────────────────

def _legend_patches():
    items = [
        (C_OS,      "OuterShell"),
        (C_IS,      "InnerShell"),
        (C_FP,      "FootPlate"),
        (C_EC,      "ElevatorCylinder"),
        (C_HC,      "HorizontalCylinder"),
        (C_WHEEL,   "Wheel (Ø 70 mm)"),
        (C_PAYLOAD, "Payload"),
        (C_STAIR,   "Stair"),
    ]
    return [mpatches.Patch(facecolor=c, edgecolor="black", linewidth=0.8, label=l)
            for c, l in items]


# ── Main figure ───────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(18, 13))
fig.suptitle(
    "TreppenSchlepper — 4 Climbing Phases (3-D isometric view)\n"
    "18/27 stair  |  OS 250×400×140 mm  |  IS 250×370×80 mm  |  "
    "Wheel track 340 mm  |  Payload 20 kg",
    fontsize=11, fontweight="bold",
)

ax1 = fig.add_subplot(2, 2, 1, projection="3d")
ax2 = fig.add_subplot(2, 2, 2, projection="3d")
ax3 = fig.add_subplot(2, 2, 3, projection="3d")
ax4 = fig.add_subplot(2, 2, 4, projection="3d")

draw_phase1_3d(ax1)
draw_phase2_3d(ax2)
draw_phase3_3d(ax3)
draw_phase4_3d(ax4)

fig.legend(
    handles=_legend_patches(),
    loc="lower center", ncol=8, fontsize=7.5,
    frameon=True, edgecolor="gray",
    bbox_to_anchor=(0.5, 0.01),
)

plt.tight_layout(rect=[0, 0.05, 1, 0.95])

out = os.path.join("results", "phases_3d.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"3-D drawing saved -> {out}")
