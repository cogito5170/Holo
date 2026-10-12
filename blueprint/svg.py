"""작은 SVG 작성 도구 (외부 라이브러리 없이). 도면 시트(가로 A4, 표제란)와 3D 투영도 여기 있다."""
import html
import itertools
import math

import numpy as np

INK = "#1b2129"
INK2 = "#52514e"
MUTED = "#8a8f96"
GRID = "#d9dde2"
BLUE = "#2a78d6"       # 범주 1
ORANGE = "#eb6834"     # 범주 2
AQUA = "#1baf7a"       # 범주 3
YELLOW = "#eda100"     # 범주 4
RED = "#d03b3b"        # 상태: critical
AMBER = "#fab219"      # 상태: warning
GOOD = "#0ca30c"       # 상태: good
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6",
       "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
FONT = "'Inter','WenQuanYi Zen Hei',sans-serif"

_ids = itertools.count()


def esc(s):
    return html.escape(str(s), quote=True)


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.el = []
        self.id = f"s{next(_ids)}"

    # ---------------------------------------------------------- 기본 도형
    def add(self, s):
        self.el.append(s)

    def line(self, x1, y1, x2, y2, stroke=INK, w=0.3, dash=None, cap="butt", arrow=None, opacity=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if arrow in ("end", "both"):
            m += f' marker-end="url(#{self.id}a)"'
        if arrow in ("start", "both"):
            m += f' marker-start="url(#{self.id}b)"'
        o = f' opacity="{opacity}"' if opacity != 1 else ""
        self.add(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{stroke}" stroke-width="{f(w)}" '
                 f'stroke-linecap="{cap}"{d}{m}{o}/>')

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=0.3, rx=0, dash=None, opacity=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity != 1 else ""
        self.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{f(sw)}"{d}{o}/>')

    def poly(self, pts, fill="none", stroke=INK, sw=0.3, close=True, dash=None, opacity=1, join="round"):
        p = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
        tag = "polygon" if close else "polyline"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity != 1 else ""
        self.add(f'<{tag} points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}" stroke-linejoin="{join}"{d}{o}/>')

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=0.3, dash=None, opacity=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity != 1 else ""
        self.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}"{d}{o}/>')

    def text(self, x, y, s, size=3.0, anchor="start", fill=INK, weight=None, rotate=None, italic=False, baseline=None):
        a = f' font-weight="{weight}"' if weight else ""
        r = f' transform="rotate({f(rotate)} {f(x)} {f(y)})"' if rotate else ""
        i = ' font-style="italic"' if italic else ""
        b = f' dominant-baseline="{baseline}"' if baseline else ""
        self.add(f'<text x="{f(x)}" y="{f(y)}" font-size="{f(size)}" text-anchor="{anchor}" fill="{fill}"{a}{r}{i}{b}>{esc(s)}</text>')

    def lines(self, x, y, rows, size=3.0, lh=1.45, **kw):
        for i, r in enumerate(rows):
            self.text(x, y + i * size * lh, r, size=size, **kw)

    def arrow(self, x1, y1, x2, y2, stroke=INK, w=0.35, dash=None):
        self.line(x1, y1, x2, y2, stroke=stroke, w=w, dash=dash, arrow="end")

    def dim(self, x1, y1, x2, y2, off, label, size=2.6, color=INK2):
        """치수선: 두 점 사이, 법선 방향으로 off 만큼 띄운다."""
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        a1 = (x1 + nx * off, y1 + ny * off)
        a2 = (x2 + nx * off, y2 + ny * off)
        ext = 1.2 if off >= 0 else -1.2
        self.line(x1 + nx * 0.8 * (1 if off >= 0 else -1), y1 + ny * 0.8 * (1 if off >= 0 else -1),
                  a1[0] + nx * ext, a1[1] + ny * ext, stroke=color, w=0.18)
        self.line(x2 + nx * 0.8 * (1 if off >= 0 else -1), y2 + ny * 0.8 * (1 if off >= 0 else -1),
                  a2[0] + nx * ext, a2[1] + ny * ext, stroke=color, w=0.18)
        self.line(*a1, *a2, stroke=color, w=0.22, arrow="both")
        mx, my = (a1[0] + a2[0]) / 2, (a1[1] + a2[1]) / 2
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90 or ang < -90:
            ang += 180
        sgn = 1 if off >= 0 else -1
        self.text(mx + nx * 1.4 * sgn, my + ny * 1.4 * sgn + (size * 0.35 if abs(ang) < 1 and sgn > 0 else 0), label,
                  size=size, anchor="middle", fill=color, rotate=ang if abs(ang) > 0.5 else None,
                  baseline="middle" if abs(ang) > 0.5 else None)

    def render(self, cls="", style=""):
        defs = (f'<defs><marker id="{self.id}a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" '
                f'orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="context-stroke"/></marker>'
                f'<marker id="{self.id}b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" '
                f'orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="context-stroke"/></marker></defs>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(self.w)} {f(self.h)}" class="{cls}" '
                f'style="font-family:{FONT};{style}">{defs}{"".join(self.el)}</svg>')


# ================================================================== 도면 시트
def sheet(no, title, scale, date, rev, project):
    """가로 A4 도면 시트 (297 x 210). 표제란에 '설계 제안 — 미검증'."""
    s = Svg(297, 210)
    s.rect(5, 5, 287, 200, stroke=INK, sw=0.6)
    s.rect(7, 7, 283, 196, stroke=INK, sw=0.2)
    x0, y0, w, h = 167, 175, 123, 28
    s.rect(x0, y0, w, h, fill="#ffffff", stroke=INK, sw=0.4)
    s.line(x0, y0 + 7, x0 + w, y0 + 7, w=0.2)
    s.line(x0, y0 + 14, x0 + w, y0 + 14, w=0.2)
    s.line(x0, y0 + 21, x0 + w, y0 + 21, w=0.2)
    s.line(x0 + 62, y0 + 14, x0 + 62, y0 + 28, w=0.2)
    s.line(x0 + 92, y0 + 14, x0 + 92, y0 + 28, w=0.2)
    s.text(x0 + 2, y0 + 5, project, size=3.0, weight="700")
    s.text(x0 + 2, y0 + 12, title, size=3.1, weight="700")
    s.text(x0 + 2, y0 + 19.2, f"도면번호 {no}", size=2.6)
    s.text(x0 + 64, y0 + 19.2, f"rev {rev}", size=2.6)
    s.text(x0 + 94, y0 + 19.2, date, size=2.6)
    s.text(x0 + 2, y0 + 26.2, "설계 제안 — 미검증", size=2.6, fill=RED, weight="700")
    s.text(x0 + 64, y0 + 26.2, f"척도 {scale}", size=2.6)
    s.text(x0 + 94, y0 + 26.2, "단위 mm", size=2.6)
    return s


# ================================================================== 3D 투영
class Camera:
    def __init__(self, eye, target, focal=1.0, up=(0, 1, 0)):
        self.e = np.asarray(eye, float)
        fwd = np.asarray(target, float) - self.e
        self.f = fwd / np.linalg.norm(fwd)
        r = np.cross(self.f, np.asarray(up, float))
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)
        self.focal = focal

    def proj(self, p):
        v = np.asarray(p, float) - self.e
        z = np.dot(v, self.f)
        return np.array([self.focal * np.dot(v, self.r) / z, -self.focal * np.dot(v, self.u) / z]), z

    def depth(self, p):
        return float(np.dot(np.asarray(p, float) - self.e, self.f))


def shade(hex_color, k):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    k = max(0.0, min(1.4, k))
    return "#%02x%02x%02x" % tuple(min(255, int(c * k)) for c in (r, g, b))


class Scene:
    """다각형 면 목록 → 화가 알고리즘(깊이 정렬)으로 그린다. 좌표는 (x, y, z) mm."""

    def __init__(self, cam, light=(-0.35, 0.8, 0.5)):
        self.cam = cam
        self.faces = []      # (depth, kind, payload)
        L = np.asarray(light, float)
        self.light = L / np.linalg.norm(L)

    def face(self, pts, color, stroke=None, cull=True, k=None, opacity=1.0, bias=0.0):
        P = np.asarray(pts, float)
        n = np.cross(P[1] - P[0], P[2] - P[0])
        nn = np.linalg.norm(n)
        if nn == 0:
            return
        n = n / nn
        centre = P.mean(axis=0)
        if cull and np.dot(n, self.cam.e - centre) <= 0:
            return
        lit = k if k is not None else 0.55 + 0.5 * abs(np.dot(n, self.light))
        self.faces.append((self.cam.depth(centre) + bias, "poly", (P, shade(color, lit), stroke, opacity)))

    def extrude(self, profile_yz, x0, x1, color, stroke="#00000033", cap_color=None):
        """(y, z) 단면을 x0..x1 로 밀어 만든 입체."""
        pr = list(profile_yz)
        cap0 = [(x0, y, z) for y, z in pr]
        cap1 = [(x1, y, z) for y, z in pr][::-1]
        self.face(cap0[::-1], cap_color or color, stroke)
        self.face(cap1[::-1], cap_color or color, stroke)
        for (ya, za), (yb, zb) in zip(pr, pr[1:] + pr[:1]):
            self.face([(x0, ya, za), (x0, yb, zb), (x1, yb, zb), (x1, ya, za)], color, stroke)

    def box(self, x0, x1, y0, y1, z0, z1, color, stroke="#00000033"):
        self.extrude([(y0, z0), (y1, z0), (y1, z1), (y0, z1)], x0, x1, color, stroke)

    def item(self, depth, svg_fragment_fn):
        """깊이를 가진 임의 그리기 (점·글자·선)."""
        self.faces.append((depth, "fn", svg_fragment_fn))

    def render(self, s, ox, oy, scale):
        def to2(p):
            q, _ = self.cam.proj(p)
            return (ox + q[0] * scale, oy + q[1] * scale)
        for depth, kind, pay in sorted(self.faces, key=lambda t: -t[0]):
            if kind == "poly":
                P, col, stroke, op = pay
                s.poly([to2(p) for p in P], fill=col, stroke=stroke or col, sw=0.12, opacity=op)
            else:
                pay(s, to2)
