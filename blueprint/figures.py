"""HOLO-D1 그림: 계산 렌더 2장 · 모델 차트 · UI 시트 · 일정. 모든 값은 spec.py / model.py 에서 온다."""
import base64
import io
import math

import numpy as np

from blueprint import drawings as DW
from blueprint import spec as S
from blueprint.svg import (AMBER, AQUA, BLUE, GOOD, GRID, INK, INK2, MUTED, ORANGE, RED, SEQ, YELLOW, Camera, Scene,
                           Svg, f)


# ================================================================== 계산 렌더
def _icosa():
    t = (1 + 5 ** 0.5) / 2
    v = np.array([[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
                  [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]], float)
    v /= np.linalg.norm(v[0])
    fcs = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
           (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    return v, fcs


def _model_faces(img, angle=0.6):
    """3D 모델(정이십면체)을 모델 영역 안 2D 다각형들로 (상 평면 좌표 x, y)."""
    v, fcs = _icosa()
    ry, rx = angle, 0.45
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    w = v @ (Rx @ Ry).T
    mb = S.MODEL_BOX
    cx, cy = (mb["x0"] + mb["x1"]) / 2, img["center"][0] + (mb["y0"] + mb["y1"]) / 2
    rad = 0.42 * min(mb["x1"] - mb["x0"], mb["y1"] - mb["y0"])
    L = np.array([-0.4, 0.7, 0.6])
    L /= np.linalg.norm(L)
    out = []
    for a, b, c in fcs:
        n = np.cross(w[b] - w[a], w[c] - w[a])
        n /= np.linalg.norm(n)
        if n[2] <= 0:
            continue
        k = 0.35 + 0.75 * max(0.0, float(np.dot(n, L)))
        col = "#%02x%02x%02x" % tuple(min(255, int(ch * k)) for ch in (120, 190, 255))
        pts = [(cx + rad * w[i][0], cy + rad * w[i][1]) for i in (a, b, c)]
        out.append((float(np.mean([w[i][2] for i in (a, b, c)])), pts, col))
    out.sort(key=lambda t: t[0])
    return out


def _disc(cx, cy, cz, r, n=14, plane="y"):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        if plane == "y":
            pts.append((cx + r * math.cos(a), cy, cz + r * math.sin(a)))
        else:
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz))
    return pts


def render(r, eye, target, w=180, h=118, finger=False, active=1):
    img = r["img"]
    cam = Camera(eye, target)
    sc = Scene(cam)
    W2 = S.BODY["W"] / 2
    (my0, mz0), (my1, mz1) = S.mirror_endpoints()
    # 책상
    zn = eye[2] - 120.0                                     # 카메라 뒤로 넘어가는 책상 부분은 그리지 않는다
    sc.face([(-900, 0, -700), (900, 0, -700), (900, 0, zn), (-900, 0, zn)], "#e4dfd6", cull=False, k=1.0, bias=5000)
    # 본체 (측면 단면을 x 로 밀기). 미러 면은 어두운 유리색
    prof = DW.body_profile()
    for x0 in (-W2, W2):
        cap = [(x0, y, z) for y, z in prof]
        sc.face(cap if x0 > 0 else cap[::-1], "#34383e")
    for (ya, za), (yb, zb) in zip(prof, prof[1:] + prof[:1]):
        is_mirror = {(round(ya, 1), round(za, 1)), (round(yb, 1), round(zb, 1))} == {(round(my0, 1), round(mz0, 1)), (round(my1, 1), round(mz1, 1))}
        col = "#1d2733" if is_mirror else "#3a3f46"
        sc.face([(-W2, ya, za), (-W2, yb, zb), (W2, yb, zb), (W2, ya, za)], col, k=0.95 if is_mirror else None)
    # 후드
    sc.box(-W2, W2, S.VISOR["y"] - 3, S.VISOR["y"], mz1, S.VISOR["z_front"], "#2b2f35")
    # 레지 위 부품
    H = S.HAPTIC
    for iz in range(H["n_z"]):
        for ix in range(H["n_x"]):
            x = H["x_center"] + (ix - (H["n_x"] - 1) / 2) * H["pitch"]
            z = img["z"] + (iz - (H["n_z"] - 1) / 2) * H["pitch"]
            sc.face(_disc(x, H["top_y"], z, H["elem_d"] / 2), "#c9ced5", cull=False, k=1.0)
            sc.face(_disc(x, H["top_y"] + 0.2, z, H["elem_d"] / 2 * 0.62), "#5d646d", cull=False, k=1.0, bias=-0.5)
    tx, tz = S.TRACKER["x"], S.TRACKER["z"]
    sc.box(tx - 40, tx + 40, S.LEDGE["H"], S.LEDGE["H"] + 12, tz - 15, tz + 15, "#15181c")
    ex, ez = S.ESTOP["x"], S.ESTOP["z"]
    sc.face(_disc(ex, S.LEDGE["H"] + 0.5, ez, 16, 20), "#e8b400", cull=False, k=1.0)
    sc.box(ex - 8, ex + 8, S.LEDGE["H"], S.LEDGE["H"] + 18, ez - 8, ez + 8, "#2a2d31")
    sc.face(_disc(ex, S.LEDGE["H"] + 20, ez, S.ESTOP["d"] / 2 + 1, 20), "#d03b3b", cull=False, k=1.0)
    # 공중 상 내용 (빛나는 부분만; 검정 = 공기)
    zi = img["z"]
    faces = _model_faces(img)
    btn = r["buttons"]

    def draw_image(s, to2):
        for _, pts, col in faces:
            s.poly([to2((x, y, zi)) for x, y in pts], fill=col, stroke=col, sw=0.1)
        for i, (bx, by) in enumerate(btn):
            ring = [to2(p) for p in _disc(bx, by, zi, S.BUTTONS["d"] / 2, 28, plane="z")]
            hot = i == active
            s.poly(ring, fill="#7fd1ff" if hot else "#ffffff", stroke="#e8f6ff", sw=0.45 if hot else 0.3,
                   opacity=0.35 if hot else 0.07)
            s.poly(ring, fill="none", stroke="#bfe8ff" if hot else "#eef3f8", sw=0.55 if hot else 0.35)
            if hot:
                s.poly([to2(p) for p in _disc(bx, by, zi, S.BUTTONS["d"] / 2 + 3.5, 28, plane="z")], stroke="#9fdcff", sw=0.25, opacity=0.7)
            c = to2((bx, by - 2.2, zi))
            top, bot = to2((bx, by + 3, zi)), to2((bx, by - 3, zi))
            size = abs(bot[1] - top[1]) * 0.95
            s.text(c[0], c[1], S.BUTTONS["labels"][i], size=size, anchor="middle", fill="#ffffff", weight="700")

    sc.item(cam.depth((0, img["center"][0], zi)) - 1, draw_image)
    if finger:
        bx, by = btn[active]
        tip = (bx, by - 2, zi + 4)
        knuckle = (bx + 4, by - 10, zi + 80)
        wrist = (bx + 22, by - 45, zi + 190)

        def draw_hand(s, to2):
            a, b, c = to2(tip), to2(knuckle), to2(wrist)
            wf = abs(to2((bx, by, zi + 60))[0] - to2((bx + 16, by, zi + 60))[0])
            s.add(f'<path d="M{f(c[0])},{f(c[1])} L{f(b[0])},{f(b[1])}" stroke="#c99476" stroke-width="{f(wf * 2.6)}" stroke-linecap="round" fill="none"/>')
            s.add(f'<path d="M{f(b[0])},{f(b[1])} L{f(a[0])},{f(a[1])}" stroke="#d8a487" stroke-width="{f(wf)}" stroke-linecap="round" fill="none"/>')
        sc.item(cam.depth(knuckle) - 2000, draw_hand)
    # 맞춤: 본체 윤곽 점으로 경계 상자
    pts = []
    for x0 in (-W2, W2):
        for y, z in prof + [(S.VISOR["y"], S.VISOR["z_front"])]:
            pts.append(cam.proj((x0, y, z))[0])
    P = np.array(pts)
    lo, hi = P.min(axis=0), P.max(axis=0)
    margin = 8
    scale = min((w - 2 * margin) / (hi[0] - lo[0]), (h - 2 * margin) / (hi[1] - lo[1]))
    ox = w / 2 - scale * (lo[0] + hi[0]) / 2
    oy = h / 2 - scale * (lo[1] + hi[1]) / 2
    s = Svg(w, h)
    s.rect(0, 0, w, h, fill="#f4f1ec", stroke="none")
    sc.render(s, ox, oy, scale)
    return s.render(cls="fig")


# ================================================================== 차트 공통
def _axes(s, x0, y0, x1, y1, xt, yt, xl, yl, fx, fy, xlab, ylab, size=2.6):
    for v in yt:
        y = fy(v)
        s.line(x0, y, x1, y, stroke=GRID, w=0.18)
        s.text(x0 - 1.5, y + 0.9, yl(v), size=size, anchor="end", fill=INK2)
    for v in xt:
        x = fx(v)
        s.line(x, y1, x, y1 + 1.2, stroke=INK2, w=0.2)
        s.text(x, y1 + 4.2, xl(v), size=size, anchor="middle", fill=INK2)
    s.line(x0, y1, x1, y1, stroke=INK2, w=0.3)
    s.text((x0 + x1) / 2, y1 + 9, xlab, size=size + 0.1, anchor="middle", fill=INK)
    s.text(x0, y0 - 3.5, ylab, size=size + 0.1, anchor="start", fill=INK)


def _tw(t, size):
    return sum(size * (0.92 if ord(ch) > 127 else 0.55) for ch in t)


def _legend(s, x, y, items, size=2.6, gap=4):
    cx = x
    for col, label, dash in items:
        s.line(cx, y, cx + 6, y, stroke=col, w=0.8, dash=dash, cap="round")
        s.text(cx + 7.5, y + 0.95, label, size=size, fill=INK)
        cx += 7.5 + _tw(label, size) + gap


def contrast_chart(r):
    s = Svg(170, 100)
    x0, y0, x1, y1 = 20, 16, 138, 84
    Lmax = 2000.0
    fx = lambda L: x0 + (x1 - x0) * L / Lmax
    fy = lambda C: y1 - (y1 - y0) * (math.log10(C) - 0) / 2.0          # 1 .. 100
    _axes(s, x0, y0, x1, y1, [0, 500, 1000, 1500, 2000], [1, 2, 3, 5, 10, 20, 50, 100], lambda v: f"{v:.0f}",
          lambda v: f"{v:g}", fx, fy, "패널 휘도 (cd/m²)", "대비 (공중 상 : 배경)")
    s.line(x0, fy(3), x1, fy(3), stroke=INK2, w=0.3, dash="1.5,1")
    s.text(x0 + 1, fy(3) - 1.2, "OPT-02 목표 3 : 1", size=2.4, fill=INK2)
    s.line(fx(S.PANEL["L_max"]), y0, fx(S.PANEL["L_max"]), y1, stroke=INK2, w=0.25, dash="0.8,0.8")
    s.text(fx(S.PANEL["L_max"]) + 1, y0 + 2.5, "패널 목표 1000", size=2.3, fill=INK2)
    from blueprint import model as M
    series = [("prism", True, BLUE, "프리즘 · 후드"), ("prism", False, ORANGE, "프리즘 · 후드 없음"),
              ("bead", True, AQUA, "비드 · 후드"), ("bead", False, YELLOW, "비드 · 후드 없음")]
    ends = []
    for sheet, hood, col, lab in series:
        Ls = np.linspace(20, Lmax, 120)
        C = [min(100.0, M.contrast(L, sheet, hood)) for L in Ls]
        s.poly([(fx(L), fy(c)) for L, c in zip(Ls, C)], stroke=col, sw=0.6, close=False)
        ends.append([fy(C[-1]), lab, col])
    ends.sort()
    for i in range(1, len(ends)):
        if ends[i][0] - ends[i - 1][0] < 3.4:
            ends[i][0] = ends[i - 1][0] + 3.4
    for y, lab, col in ends:
        s.circle(x1, y, 0.0)
        s.text(x1 + 1.5, y + 0.9, lab, size=2.4, fill=INK)
    _legend(s, x0, 7, [(c, l, None) for _, _, c, l in series], size=2.4, gap=2)
    return s.render(cls="fig")


def _png_heat(amp, vmax):
    from PIL import Image
    ramp = [tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) for h in ["#fcfcfb"] + SEQ]
    a = np.clip(amp / vmax, 0, 1)
    idx = a * (len(ramp) - 1)
    lo = np.floor(idx).astype(int)
    hi = np.minimum(lo + 1, len(ramp) - 1)
    t = (idx - lo)[..., None]
    R = np.array(ramp, float)
    rgb = (R[lo] * (1 - t) + R[hi] * t).astype(np.uint8)
    im = Image.fromarray(rgb[::-1], "RGB")
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def acoustic_chart(r):
    c = r["acoustic"]["cases"]["center"]
    xg, yg, amp = c["grid"]
    img = r["img"]
    s = Svg(170, 138)
    x0, y0, x1, y1 = 22, 12, 112, 12 + 90 * (yg[-1] - yg[0]) / (xg[-1] - xg[0])
    fx = lambda x: x0 + (x1 - x0) * (x - xg[0]) / (xg[-1] - xg[0])
    fy = lambda y: y1 - (y1 - y0) * (y - yg[0]) / (yg[-1] - yg[0])
    data = _png_heat(amp, c["p_peak"])
    s.add(f'<image x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" preserveAspectRatio="none" href="data:image/png;base64,{data}"/>')
    s.rect(x0, y0, x1 - x0, y1 - y0, stroke=INK2, sw=0.25)
    for v in range(-50, 141, 50):
        s.text(fx(v), y1 + 4, f"{v}", size=2.4, anchor="middle", fill=INK2)
    for v in range(250, int(yg[-1]) + 1, 50):
        s.text(x0 - 1.2, fy(v) + 0.9, f"{v}", size=2.4, anchor="end", fill=INK2)
    s.text((x0 + x1) / 2, y1 + 8.5, "x (mm)", size=2.6, anchor="middle")
    s.text(x0, y0 - 3, "책상 위 높이 y (mm) — 상 평면 z = 70", size=2.6)
    xl = max(-img["width"] / 2, xg[0])
    s.rect(fx(xl), fy(img["top"]), (fx(img["width"] / 2) - fx(xl)), fy(img["bottom"]) - fy(img["top"]),
           stroke=AQUA, sw=0.35, dash="1,0.7")
    for bx, by in r["buttons"]:
        s.circle(fx(bx), fy(by), S.BUTTONS["d"] / 2 * (x1 - x0) / (xg[-1] - xg[0]), stroke=INK, sw=0.25)
    bx, by = c["focus"]
    s.line(fx(bx) - 1.6, fy(by), fx(bx) + 1.6, fy(by), stroke=RED, w=0.4)
    s.line(fx(bx), fy(by) - 1.6, fx(bx), fy(by) + 1.6, stroke=RED, w=0.4)
    s.circle(fx(c["peak"][0]), fy(c["peak"][1]), 0.9, fill=INK, stroke="#ffffff", sw=0.25)
    lgx, lgy = x0 + 2, y0 + 4
    s.rect(lgx - 1, lgy - 3, 54, 10, fill="#ffffff", stroke="none", opacity=0.85)
    s.line(lgx, lgy - 0.9, lgx + 3.2, lgy - 0.9, stroke=RED, w=0.4)
    s.line(lgx + 1.6, lgy - 2.5, lgx + 1.6, lgy + 0.7, stroke=RED, w=0.4)
    s.text(lgx + 5, lgy, "목표 초점 (버튼 2)", size=2.3)
    s.circle(lgx + 1.6, lgy + 4, 0.9, fill=INK, stroke="#ffffff", sw=0.25)
    s.text(lgx + 5, lgy + 4.9, "모델 최대 음압 위치", size=2.3)
    s.text(fx(img["width"] / 2) - 1, fy(img["top"]) + 3, "공중 상", size=2.3, anchor="end", fill=AQUA)
    # 색 막대
    cx0, cy0 = x0, y1 + 13
    for i, col in enumerate(["#fcfcfb"] + SEQ):
        s.rect(cx0 + i * 5, cy0, 5, 2.6, fill=col, stroke="none")
    s.rect(cx0, cy0, 5 * (len(SEQ) + 1), 2.6, stroke=INK2, sw=0.15)
    s.text(cx0, cy0 + 6, "0", size=2.3, fill=INK2)
    s.text(cx0 + 5 * (len(SEQ) + 1), cy0 + 6, f"{c['p_peak'] / 1e3:.2f} kPa rms", size=2.3, anchor="end", fill=INK2)
    s.text(cx0 + 5 * (len(SEQ) + 1) + 2, cy0 + 2.2, "음압 진폭 |p| (모델)", size=2.3, fill=INK)
    # 가로 단면 (초점 높이)
    px0, py0, px1, py1 = 124, 22, 166, 70
    s.text(px0, py0 - 5, "초점 높이에서 x 단면", size=2.6)
    s.text(px0, py0 - 1.8, "(최대값으로 정규화)", size=2.3, fill=INK2)
    fxp = lambda x: px0 + (px1 - px0) * (x - xg[0]) / (xg[-1] - xg[0])
    fyp = lambda v: py1 - (py1 - py0) * v
    for v in (0, 0.5, 1.0):
        s.line(px0, fyp(v), px1, fyp(v), stroke=GRID, w=0.18)
        s.text(px0 - 1, fyp(v) + 0.9, f"{v:g}", size=2.2, anchor="end", fill=INK2)
    for v in (-50, 50, 140):
        s.text(fxp(v), py1 + 3.8, f"{v}", size=2.2, anchor="middle", fill=INK2)
    for name, col, lab in (("center", BLUE, "버튼 2 (조향 0°)"), ("edge", ORANGE, "버튼 1 (최대 조향)")):
        cc = r["acoustic"]["cases"][name]
        xg2, yg2, a2 = cc["grid"]
        iy = np.argmin(np.abs(yg2 - cc["peak"][1]))
        row = a2[iy] / cc["p_peak"]
        s.poly([(fxp(x), fyp(v)) for x, v in zip(xg2, row)], stroke=col, sw=0.5, close=False)
    _legend(s, px0, py1 + 9, [(BLUE, "버튼 2 (0°)", None)], size=2.3)
    _legend(s, px0, py1 + 13, [(ORANGE, f"버튼 1 ({r['acoustic']['cases']['edge']['steer_deg']:.1f}°)", None)], size=2.3)
    return s.render(cls="fig")


def sweep_chart(r):
    s = Svg(150, 70)
    x0, y0, x1, y1 = 18, 12, 140, 56
    data = r["sweep"]
    fy = lambda v: y1 - (y1 - y0) * v / 20.0
    for v in (0, 5, 10, 15, 20):
        s.line(x0, fy(v), x1, fy(v), stroke=GRID, w=0.18)
        s.text(x0 - 1.5, fy(v) + 0.9, f"±{v}°", size=2.4, anchor="end", fill=INK2)
    bw = (x1 - x0) / len(data)
    for i, (W, hdeg) in enumerate(data):
        x = x0 + i * bw + bw * 0.25
        chosen = abs(W - S.BODY["W"]) < 1e-6
        s.add(f'<path d="M{f(x)},{f(y1)} V{f(fy(hdeg) + 1)} q0,-1 1,-1 H{f(x + bw * 0.5 - 1)} q1,0 1,1 V{f(y1)} z" fill="{BLUE if chosen else "#86b6ef"}"/>')
        s.text(x + bw * 0.25, fy(hdeg) - 1.5, f"±{hdeg:.1f}°", size=2.4, anchor="middle", fill=INK)
        s.text(x + bw * 0.25, y1 + 4.2, f"{W}", size=2.4, anchor="middle", fill=INK if chosen else INK2, weight="700" if chosen else None)
    s.line(x0, y1, x1, y1, stroke=INK2, w=0.3)
    s.line(x0, fy(15), x1, fy(15), stroke=INK2, w=0.3, dash="1.5,1")
    s.text(x1, fy(15) - 1.2, "OPT-03 목표 ±15°", size=2.3, anchor="end", fill=INK2)
    s.text((x0 + x1) / 2, y1 + 9, "본체 폭 (mm) — 진한 막대가 채택값", size=2.6, anchor="middle")
    s.text(x0, y0 - 4, "상 전체가 보이는 수평 시야 반각 (모델)", size=2.6)
    return s.render(cls="fig")


def latency_chart(r):
    lat = r["lat"]
    s = Svg(170, 92)
    x0, x1 = 58, 160
    tmax = 120.0
    fx = lambda t: x0 + (x1 - x0) * t / tmax
    y = 12
    for title, rows, col, target, tlabel in (("손 → 시각 피드백 (hover)", lat["visual"], BLUE, S.LAT_TARGET["visual"], "PR-02 ≤ 100 ms"),
                                             ("손 → 촉감 (누름 → activate → 햅틱)", lat["haptic"], ORANGE, None, None)):
        s.text(4, y, title, size=2.7, weight="700")
        y += 3
        t = 0.0
        y_start = y
        for name, v in rows:
            s.text(x0 - 2, y + 2.4, name, size=2.35, anchor="end", fill=INK2)
            s.add(f'<rect x="{f(fx(t))}" y="{f(y)}" width="{f(max(0.4, fx(t + v) - fx(t) - 0.4))}" height="3.2" rx="0.6" fill="{col}"/>')
            s.text(fx(t + v) + 1, y + 2.4, f"{v:.1f}", size=2.25, fill=INK)
            t += v
            y += 4.6
        if target:
            s.line(fx(target), y_start - 1, fx(target), y - 1, stroke=INK2, w=0.3, dash="1.2,0.8")
            s.text(fx(target) + 1, y_start - 1.2, tlabel, size=2.25, fill=INK2)
        s.text(x1, y + 1.5, f"합계 {t:.1f} ms", size=2.5, anchor="end", weight="700")
        y += 8
    for v in (0, 20, 40, 60, 80, 100, 120):
        s.text(fx(v), y - 2, f"{v}", size=2.2, anchor="middle", fill=INK2)
    s.text((x0 + x1) / 2, y + 2, "누적 시간 (ms) — 값은 모두 가정 [A], 음파 비행만 계산 [C]", size=2.4, anchor="middle")
    return s.render(cls="fig")


def power_chart(r):
    s = Svg(160, 62)
    x0, x1 = 50, 140
    pmax = 9.0
    fx = lambda p: x0 + (x1 - x0) * p / pmax
    _legend(s, x0, 6, [(BLUE, "평균", None), (ORANGE, "피크", None)], size=2.5)
    y = 12
    for name, (a, p) in S.POWER.items():
        s.text(x0 - 2, y + 4, name, size=2.4, anchor="end", fill=INK2)
        s.add(f'<rect x="{f(x0)}" y="{f(y)}" width="{f(fx(a) - x0)}" height="2.8" rx="0.6" fill="{BLUE}"/>')
        s.add(f'<rect x="{f(x0)}" y="{f(y + 3.3)}" width="{f(fx(p) - x0)}" height="2.8" rx="0.6" fill="{ORANGE}"/>')
        s.text(fx(a) + 1, y + 2.3, f"{a:.1f}", size=2.2)
        s.text(fx(p) + 1, y + 5.6, f"{p:.1f}", size=2.2)
        y += 8.2
    s.line(x0, 11, x0, y, stroke=INK2, w=0.3)
    s.text(x1, y + 3, f"합계 평균 {r['power']['avg']:.1f} W · 피크 {r['power']['peak']:.1f} W (W, 가정 [A])", size=2.4, anchor="end")
    return s.render(cls="fig")


# ================================================================== UI
def ui_states():
    s = Svg(170, 78)
    states = [("idle", "대기", "#7d8792", None, "얇은 회색 테두리"),
              ("hover", "hover", "#e8eef4", None, "밝은 테두리 · 1.1배"),
              ("arm", "arm", "#ffffff", "half", "테두리가 반쯤 차오름 · 약한 펄스"),
              ("activate", "activate", "#ffffff", "fill", "흰 채움 + 물결 · 클릭 패턴"),
              ("tracking-lost", "추적 상실", AMBER, "dash", "앰버 점선 · 손 아이콘 · 햅틱 정지"),
              ("safety-stop", "안전 정지", RED, "stop", "빨강 고리 · 정지 아이콘 · 햅틱 차단")]
    for i, (key, name, col, mode, desc) in enumerate(states):
        cx = 6 + (i % 3) * 54
        cy = 4 + (i // 3) * 37
        s.rect(cx, cy, 50, 33, fill="#0b0d10", stroke="none", rx=1.5)
        x, y, rr = cx + 25, cy + 13, 7.0 * (1.1 if key == "hover" else 1.0)
        if mode == "fill":
            s.circle(x, y, rr + 3.2, stroke="#9fdcff", sw=0.3, opacity=0.8)
            s.circle(x, y, rr, fill="#ffffff", stroke="#ffffff", sw=0.6)
        elif mode == "half":
            s.circle(x, y, rr, stroke="#5b6570", sw=0.6)
            s.add(f'<path d="M{f(x)},{f(y - rr)} A{f(rr)},{f(rr)} 0 0 1 {f(x)},{f(y + rr)}" stroke="#ffffff" stroke-width="0.9" fill="none"/>')
        elif mode == "dash":
            s.circle(x, y, rr, stroke=col, sw=0.6, dash="1.4,1")
            s.text(x, y + 1.3, "✋", size=4, anchor="middle", fill=col)
        elif mode == "stop":
            s.circle(x, y, rr, stroke=col, sw=1.0)
            s.rect(x - 2.5, y - 2.5, 5, 5, fill=col, stroke="none")
        else:
            s.circle(x, y, rr, stroke=col, sw=0.5 if key == "idle" else 0.7)
        s.text(cx + 25, cy + 26, name, size=2.8, anchor="middle", fill="#ffffff", weight="700")
        s.text(cx + 25, cy + 30.5, desc, size=2.15, anchor="middle", fill="#c3c9d1")
    return s.render(cls="fig")


def ui_flow(r):
    s = Svg(170, 102)
    img = r["img"]
    sw_, sh_ = 50, 50 * img["height"] / img["width"]
    screens = [
        ("① 대기 (손 없음)", "model", "손을 버튼 가까이 가져오세요"),
        ("② 조작", "buttons", None),
        ("③ 추적 상실", "lost", "손이 보이지 않습니다"),
        ("④ 안전 정지", "stop", "운영자 확인이 필요합니다"),
        ("⑤ 정렬 (운영자)", "calib", "표적 4개를 차례로 누르세요"),
    ]
    pos = [(4, 8), (60, 8), (116, 8), (32, 62), (88, 62)]
    for (title, kind, msg), (x, y) in zip(screens, pos):
        s.rect(x, y, sw_, sh_, fill="#0b0d10", stroke="none", rx=1.2)
        s.text(x, y - 2, title, size=2.6, weight="700")
        k = sw_ / img["width"]
        X = lambda xx: x + sw_ / 2 + xx * k
        Y = lambda yy: y + sh_ / 2 - (yy - img["center"][0]) * k
        if kind in ("model", "buttons", "lost"):
            for _, pts, col in _model_faces(img, angle=0.6 if kind != "buttons" else 1.0):
                s.poly([(X(px), Y(py)) for px, py in pts], fill=col if kind != "lost" else "#4a5561", stroke="none")
        if kind in ("buttons", "lost", "model"):
            for i, (bx, by) in enumerate(r["buttons"]):
                col = "#eef3f8" if kind == "buttons" else ("#6b7580" if kind == "model" else AMBER)
                dash = "0.8,0.6" if kind == "lost" else None
                s.circle(X(bx), Y(by), S.BUTTONS["d"] / 2 * k, stroke=col, sw=0.35, dash=dash,
                         fill="#ffffff" if (kind == "buttons" and i == 1) else "none")
        if kind == "stop":
            s.circle(x + sw_ / 2, y + sh_ / 2 - 2, 6, stroke=RED, sw=0.9)
            s.rect(x + sw_ / 2 - 2.2, y + sh_ / 2 - 4.2, 4.4, 4.4, fill=RED, stroke="none")
        if kind == "calib":
            for cx, cy in ((-60, 30), (60, 30), (-60, -30), (60, -30)):
                xx, yy = X(cx), y + sh_ / 2 - cy * k
                s.circle(xx, yy, 2.0, stroke="#ffffff", sw=0.3)
                s.line(xx - 3, yy, xx + 3, yy, stroke="#ffffff", w=0.2)
                s.line(xx, yy - 3, xx, yy + 3, stroke="#ffffff", w=0.2)
        if msg:
            s.text(x + sw_ / 2, y + sh_ - 2, msg, size=2.1, anchor="middle", fill="#e8eef4" if kind != "stop" else "#ffb3b3")
    arrows = [((54, 22), (60, 22)), ((110, 22), (116, 22)), ((141, 8 + sh_ + 1), (84, 62 - 4)), ((60, 8 + sh_ + 1), (60, 62 - 4))]
    for a, b in arrows:
        s.line(*a, *b, stroke=INK2, w=0.3, arrow="end")
    s.lines(4, 94, ["전이: ①→② 손이 버튼에 가까워짐 · ②→③ 추적 신뢰도 < 0.6 이 150 ms · ②·③→④ 비상정지, 워치독, 과열 · ④→① 운영자 수동 해제.",
                    f"검정 = 빛 없음 = 공기(투명) — 공중 상에는 배경을 그리지 않는다. 글자 높이 ≥ {2 * r['blur']['prism']:.0f} mm (상 흐림 때문, U-001)."],
            size=2.2, fill=INK2)
    return s.render(cls="fig")


def gantt():
    s = Svg(170, 62)
    x0, x1 = 48, 164
    fx = lambda wk: x0 + (x1 - x0) * (wk - 1) / 8
    for wk in range(1, 9):
        s.text((fx(wk) + fx(wk + 1)) / 2, 6, f"{wk}주", size=2.4, anchor="middle", fill=INK2)
        s.line(fx(wk), 8, fx(wk), 8 + 6 * len(S.PLAN), stroke=GRID, w=0.15)
    for i, (name, a, b) in enumerate(S.PLAN):
        y = 9 + i * 6
        gate = "(G" in name
        s.text(x0 - 2, y + 3, name, size=2.4, anchor="end", fill=INK)
        s.add(f'<rect x="{f(fx(a) + 0.5)}" y="{f(y + 0.5)}" width="{f(fx(b + 1) - fx(a) - 1)}" height="3.6" rx="0.8" fill="{ORANGE if gate else BLUE}"/>')
    s.text(x0, 8 + 6 * len(S.PLAN) + 5, "주황 = 게이트가 있는 주 (G1 광학·햅틱 판정, G2 MVP, G3 24 h·안전)", size=2.3, fill=INK2)
    return s.render(cls="fig")


def all_figures(r):
    v = S.VIEWER
    return dict(
        render_seat=render(r, (0, v["eye_y"], v["eye_z"]), (0, r["img"]["center"][0] - 40, 0), active=1),
        render_34=render(r, (430, 560, 640), (0, 300, 0), finger=True, active=1),
        contrast=contrast_chart(r), acoustic=acoustic_chart(r), sweep=sweep_chart(r), latency=latency_chart(r),
        power=power_chart(r), ui_states=ui_states(), ui_flow=ui_flow(r), gantt=gantt(),
    )
