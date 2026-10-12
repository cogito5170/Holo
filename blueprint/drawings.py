"""HOLO-D1 도면 7장. 모든 수치는 spec.py / model.py 에서 읽는다 (그림에 숫자를 손으로 쓰지 않는다).

M-001 광학 단면도 · M-002 외형 3면도 · S-001 시스템 블록도 · S-002 외부 연결도
E-001 전원·안전 배선도 · E-002 햅틱 배열 배치도 · U-001 공중 UI 배치도 (1:1)
"""
import math

import numpy as np

from blueprint import model as M
from blueprint import spec as S
from blueprint.svg import AQUA, BLUE, GRID, INK, INK2, MUTED, ORANGE, RED, YELLOW, sheet

PROJECT = f'{S.DOC["name"]}  {S.DOC["title"]}'


def _sheet(no, title, scale):
    return sheet(no, title, scale, S.DOC["date"], S.DOC["rev"], PROJECT)


def _notes(s, x, y, rows, title="주기", size=2.55, w=None):
    s.text(x, y, title, size=2.9, weight="700")
    yy = y + 4.2
    for r in rows:
        for j, part in enumerate(_wrap(r, w or 62)):
            s.text(x + (0 if j == 0 else 3.2), yy, part, size=size, fill=INK2 if j else INK)
            yy += size * 1.42
        yy += 0.6
    return yy


def _wrap(t, n):
    out, cur = [], ""
    for word in t.split(" "):
        if len(cur) + len(word) + 1 > n and cur:
            out.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    out.append(cur)
    return out


def _f(v, d=1):
    return f"{v:.{d}f}"


def body_profile():
    """측면 외곽 (y, z) — 받침·레지·앞벽·미러 받침·미러·윗판."""
    (my0, mz0), (my1, mz1) = S.mirror_endpoints()
    D, H = S.BODY["D"], S.BODY["H"]
    return [(0.0, -D), (H, -D), (H, mz1), (my1, mz1), (my0, mz0), (my0, 0.0), (S.LEDGE["H"], 0.0),
            (S.LEDGE["H"], S.LEDGE["D"]), (0.0, S.LEDGE["D"])]


# ================================================================== M-001
def m001(r):
    img = r["img"]
    s = _sheet("M-001", "광학 단면도 (측면, x = 0)", "1:3.2")
    k = 3.2
    X = lambda z: 16 + (z + 310) / k
    Y = lambda y: 163 - y / k
    (my0, mz0), (my1, mz1) = S.mirror_endpoints()
    D, H = S.BODY["D"], S.BODY["H"]
    # 책상
    s.line(X(-320), Y(0), X(570), Y(0), w=0.5)
    for zz in range(-320, 570, 12):
        s.line(X(zz), Y(0), X(zz - 8), Y(0) + 2.2, w=0.15, stroke=MUTED)
    # 외곽
    s.poly([(X(z), Y(y)) for y, z in body_profile()], fill="#f2f4f7", stroke=INK, sw=0.45)
    # 받침 윗면 (패널 지지) · 내부 구획
    s.line(X(-D), Y(S.BASE), X(0), Y(S.BASE), w=0.2, dash="1.2,0.8", stroke=MUTED)
    # 윗판 + 후드 (무광 흑색 안쪽)
    s.rect(X(mz1), Y(H), (S.VISOR["z_front"] - mz1) / k, 3 / k, fill=INK, stroke=INK, sw=0.2)
    s.line(X(-D), Y(H - 1), X(S.VISOR["z_front"]), Y(H - 1), w=0.9, stroke="#000000")
    # 재귀반사 시트
    s.line(X(S.RETRO["z"]), Y(S.RETRO["y0"]), X(S.RETRO["z"]), Y(S.RETRO["y1"]), w=1.1, stroke=YELLOW)
    # 패널 + 루버
    pz0, pz1 = S.panel_z_range()
    s.rect(X(pz0), Y(S.PANEL["y"]), (pz1 - pz0) / k, 6 / k, fill="#2b3440", stroke=INK, sw=0.2)
    s.line(X(pz0), Y(S.PANEL["y"]) - 0.35, X(pz1), Y(S.PANEL["y"]) - 0.35, w=0.35, stroke=AQUA)
    s.line(X(pz0 + 10), Y(S.PANEL["y"] - 6), X(pz0 + 10), Y(S.BASE), w=0.3)
    s.line(X(pz1 - 10), Y(S.PANEL["y"] - 6), X(pz1 - 10), Y(S.BASE), w=0.3)
    # 미러와 그 평면
    n = np.array(S.mirror_normal())
    dvec = np.array([math.sin(math.radians(45)), -math.cos(math.radians(45))])
    a = np.array([my0, mz0]) - 120 * dvec
    b = np.array([my1, mz1]) + 60 * dvec
    s.line(X(a[1]), Y(a[0]), X(b[1]), Y(b[0]), w=0.2, dash="3,1.2,0.6,1.2", stroke=MUTED)
    s.line(X(mz0), Y(my0), X(mz1), Y(my1), w=1.0, stroke="#3d5a80")
    # 광선: 패널 중심에서 ±8°
    pc = np.array([S.PANEL["y"], S.PANEL["z_center"]])
    for ang in (-8.0, 8.0):
        t = math.radians(ang)
        d = np.array([math.cos(t), math.sin(t)])
        h, _ = M.hit_mirror(pc, d)
        d2 = M.reflect_dir(d)
        q = h + (S.RETRO["z"] - h[1]) / d2[1] * d2
        s.line(X(pc[1]), Y(pc[0]), X(h[1]), Y(h[0]), w=0.3, stroke=ORANGE, arrow="end")
        s.line(X(h[1]), Y(h[0]), X(q[1]), Y(q[0]), w=0.3, stroke=ORANGE, arrow="end")
        s.line(X(q[1]), Y(q[0]) + 0.6, X(h[1]), Y(h[0]) + 0.6, w=0.25, stroke=ORANGE, dash="1,0.7")
        ic = np.array([img["center"][0], img["z"]])
        s.line(X(h[1]), Y(h[0]), X(ic[1]), Y(ic[0]), w=0.3, stroke=ORANGE, arrow="end")
    # 공중 상
    s.line(X(img["z"]), Y(img["bottom"]), X(img["z"]), Y(img["top"]), w=1.3, stroke=AQUA)
    # 대칭 거리
    m0 = np.array([my0, mz0])
    for p, lab, side in ((pc, "d 패널", -1), (np.array([img["center"][0], img["z"]]), "d 상", 1)):
        foot = p - np.dot(p - m0, n) * n
        s.line(X(p[1]), Y(p[0]), X(foot[1]), Y(foot[0]), w=0.25, stroke=INK2, dash="0.8,0.6")
        mid = (p + foot) / 2
        s.text(X(mid[1]) + 1.5, Y(mid[0]) + (4.5 if side > 0 else -1.2), f'{lab} = {_f(img["d_panel"])}', size=2.4, fill=INK2,
               anchor="start")
    # 레지·햅틱 배열·초점
    H_ = S.HAPTIC
    hz0 = img["z"] - (H_["n_z"] - 1) / 2 * H_["pitch"] - H_["elem_d"] / 2
    hz1 = img["z"] + (H_["n_z"] - 1) / 2 * H_["pitch"] + H_["elem_d"] / 2
    s.rect(X(hz0), Y(H_["top_y"]), (hz1 - hz0) / k, 7 / k, fill="#c7ccd3", stroke=INK, sw=0.2)
    bx, by = r["buttons"][1]
    for zz in (hz0 + 5, hz1 - 5):
        s.line(X(zz), Y(H_["top_y"]), X(img["z"]), Y(by), w=0.28, stroke=BLUE, dash="1.4,0.8")
    s.circle(X(img["z"]), Y(by), 1.0, fill=BLUE, stroke=BLUE)
    s.rect(X(S.TRACKER["z"] - 15), Y(S.LEDGE["H"] + 12), 30 / k, 12 / k, stroke=MUTED, sw=0.25, dash="0.8,0.6")
    # 눈과 시선
    ex, ey = S.VIEWER["eye_z"], S.VIEWER["eye_y"]
    s.circle(X(ex), Y(ey), 1.6, fill="#ffffff", stroke=INK, sw=0.35)
    s.circle(X(ex) - 0.5, Y(ey), 0.6, fill=INK, stroke=INK)
    for yy in (img["top"], img["bottom"]):
        s.line(X(ex), Y(ey), X(img["z"]), Y(yy), w=0.22, stroke=INK2, dash="2,1")
    # 라벨
    lab = [
        (X(-D * 0.35 + mz0 * 0.65) + 4, Y(380), "하프미러 (앞 창) 45°", "start"),
        (X(S.RETRO["z"]) + 1.6, Y(90), "재귀반사 시트 (뒷벽)", "start"),
        (X(pz0), Y(S.PANEL["y"]) + 5.2, "7인치 패널 (화면 위) + 루버 필름", "start"),
        (X(img["z"]) + 2, Y(img["top"]) - 1.5, "공중 상 (실상)", "start"),
        (X(img["z"]) + 2.4, Y(by) + 0.8, "초음파 초점 (버튼 '정지')", "start"),
        ((X(hz0) + X(hz1)) / 2, Y(H_["top_y"]) + 6, "40 kHz 배열 8×8", "middle"),
        (X(-D) + 2, Y(H) - 2.2, "윗판·후드 (안쪽 무광 흑색)", "start"),
        (X(ex) - 2, Y(ey) - 3, "눈 (착석 기준)", "end"),
        ((X(0) + X(S.LEDGE["D"])) / 2, Y(S.LEDGE["H"]) + 10, "레지 (손 추적 센서는 x = -150)", "middle"),
    ]
    for x, y, t, anc in lab:
        s.text(x, y, t, size=2.55, anchor=anc)
    # 치수
    s.dim(X(-D), Y(0), X(-D), Y(H), -9, f'{_f(H, 0)}')
    s.dim(X(-D), Y(0), X(-D), Y(S.BASE), -4, f'받침 {_f(S.BASE, 0)}')
    s.dim(X(-D), Y(0), X(0), Y(0), 6, f'{_f(D, 0)}')
    s.dim(X(0), Y(0), X(S.LEDGE["D"]), Y(0), 6, f'{_f(S.LEDGE["D"], 0)}')
    s.dim(X(S.LEDGE["D"]), Y(0), X(S.LEDGE["D"]), Y(S.LEDGE["H"]), 4, f'{_f(S.LEDGE["H"], 0)}')
    s.dim(X(0), Y(img["top"]), X(img["z"]), Y(img["top"]), -4, f'{_f(img["z"], 0)}')
    v = r["view"]
    _notes(s, 160, 70, [
        "1. 광학 A2(재귀반사 공중 결상): 패널 → 하프미러 반사 → 재귀반사 시트 → 되돌아와 하프미러 투과 → 공중 상.",
        f'2. 공중 상은 미러 평면에 대해 패널과 대칭이다. d 패널 = d 상 = {_f(img["d_panel"])} mm [C]. 상 중심 높이 {_f(img["center"][0], 0)} mm, 앞면에서 {_f(img["z"], 0)} mm [C]. 패널 앞쪽 가장자리가 상의 {"아래" if img["front_edge_maps_to"] == "bottom" else "위"}쪽이 된다.',
        f'3. 서로 다른 각도의 두 광선 추적 교점과 대칭점의 차이 {img["trace_err"]:.1e} mm [C] (모델 검사).',
        f'4. 시청 영역 [C]: 눈 높이 {_f(v["eye_y_range"][0], 0)}–{_f(v["eye_y_range"][1], 0)} mm (z = {_f(S.VIEWER["eye_z"], 0)}), 수평 ±{_f(v["h_half_deg"])}°.',
        f'5. 루버 반각 {_f(r["angles"]["louver"], 0)}° [A]: 상 광선 방출각 ≤ {_f(r["angles"]["emit_max"])}° [C] 통과, 패널 직시각 ≥ {_f(r["angles"]["direct_min"])}° [C] 차단.',
        f'6. 초음파 경로와 미러 앞 모서리의 최소 간격 {_f(r["clear"]["min_gap_mm"])} mm [C].',
        "7. 모든 수치는 blueprint/spec.py · model.py 에서 계산했다.",
    ], w=50)
    # 범례
    lx, ly = 160, 156
    for i, (c, t, dash) in enumerate(((ORANGE, "빛 (패널 → 상)", None), (BLUE, "초음파", "1.4,0.8"),
                                      (INK2, "시선", "2,1"), (MUTED, "미러 평면 연장", "3,1.2,0.6,1.2"))):
        s.line(lx + i * 31, ly, lx + i * 31 + 7, ly, stroke=c, w=0.5, dash=dash)
        s.text(lx + i * 31 + 8.5, ly + 0.9, t, size=2.4)
    return s.render(cls="dwg")


# ================================================================== M-002
def m002(r):
    img = r["img"]
    s = _sheet("M-002", "외형 3면도", "1:6")
    k = 6.0
    W, D, H = S.BODY["W"], S.BODY["D"], S.BODY["H"]
    (my0, mz0), (my1, mz1) = S.mirror_endpoints()
    # 정면도
    FX = lambda x: 62 + x / k
    FY = lambda y: 98 - y / k
    s.text(FX(0), FY(H) - 11, "정면도", size=3.0, anchor="middle", weight="700")
    s.rect(FX(-W / 2), FY(H), W / k, H / k, fill="#f2f4f7", sw=0.45)
    s.rect(FX(-W / 2 + 3), FY(my1), (W - 6) / k, (my1 - my0) / k, fill="#dfe6ee", stroke="#3d5a80", sw=0.35)
    s.text(FX(0), FY(my0) - 2, "하프미러 창 (뒤로 45° 기울어짐)", size=2.4, anchor="middle", fill="#3d5a80")
    s.rect(FX(-W / 2), FY(S.LEDGE["H"]), W / k, S.LEDGE["H"] / k, fill="#e6e9ee", sw=0.4)
    s.rect(FX(-img["width"] / 2), FY(img["top"]), img["width"] / k, img["height"] / k, stroke=AQUA, sw=0.45, dash="1,0.6")
    s.text(FX(0), FY(img["bottom"]) + 3.3, "공중 상", size=2.3, anchor="middle", fill=AQUA)
    H_ = S.HAPTIC
    aw = (H_["n_x"] - 1) * H_["pitch"] + H_["elem_d"]
    s.rect(FX(H_["x_center"] - aw / 2), FY(S.LEDGE["H"] + 7), aw / k, 7 / k, fill="#c7ccd3", sw=0.2)
    s.rect(FX(S.TRACKER["x"] - 40), FY(S.LEDGE["H"] + 12), 80 / k, 12 / k, fill="#2b3440", sw=0.2)
    s.circle(FX(S.ESTOP["x"]), FY(S.LEDGE["H"] + 14), S.ESTOP["d"] / 2 / k + 0.4, fill=RED, stroke=INK, sw=0.2)
    s.dim(FX(-W / 2), FY(0), FX(W / 2), FY(0), 5, f"{W:.0f}")
    s.dim(FX(-W / 2), FY(0), FX(-W / 2), FY(H), -5, f"{H:.0f}")
    s.dim(FX(W / 2), FY(0), FX(W / 2), FY(S.LEDGE["H"]), 4, f'{S.LEDGE["H"]:.0f}')
    s.dim(FX(-img["width"] / 2), FY(img["top"]), FX(img["width"] / 2), FY(img["top"]), -3, f'{img["width"]:.1f}')
    # 측면도
    SX = lambda z: 150 + (z + D) / k
    s.text(SX(-D / 2), FY(H) - 11, "측면도 (오른쪽에서)", size=3.0, anchor="middle", weight="700")
    s.poly([(SX(z), FY(y)) for y, z in body_profile()], fill="#f2f4f7", sw=0.45)
    s.rect(SX(mz1), FY(H), (S.VISOR["z_front"] - mz1) / k, 3 / k, fill=INK, sw=0.2)
    s.line(SX(mz0), FY(my0), SX(mz1), FY(my1), w=0.8, stroke="#3d5a80")
    s.line(SX(img["z"]), FY(img["bottom"]), SX(img["z"]), FY(img["top"]), w=0.8, stroke=AQUA)
    s.dim(SX(-D), FY(0), SX(0), FY(0), 5, f"{D:.0f}")
    s.dim(SX(0), FY(0), SX(S.LEDGE["D"]), FY(0), 5, f'{S.LEDGE["D"]:.0f}')
    s.dim(SX(mz1), FY(H), SX(S.VISOR["z_front"]), FY(H), -4, f'윗판·후드 {S.VISOR["z_front"] - mz1:.0f}')
    s.text(SX(mz0) + 2, FY(my0) - 1, f'{S.MIRROR["tilt_deg"]:.0f}°', size=2.6)
    s.dim(SX(-D), FY(0), SX(-D), FY(S.BASE), -4, f"받침 {S.BASE:.0f}")
    s.text(SX(img["z"]) + 1.5, FY(img["top"]) + 2, "공중 상", size=2.3, fill=AQUA)
    # 평면도
    TY = lambda z: 126 + (z + D) / k
    s.text(FX(0), TY(-D) - 9, "평면도", size=3.0, anchor="middle", weight="700")
    s.rect(FX(-W / 2), TY(-D), W / k, (S.LEDGE["D"] + D) / k, fill="#f2f4f7", sw=0.45)
    s.line(FX(-W / 2), TY(0), FX(W / 2), TY(0), w=0.2, dash="1.2,0.8", stroke=INK2)
    s.line(FX(-W / 2), TY(S.VISOR["z_front"]), FX(W / 2), TY(S.VISOR["z_front"]), w=0.35)
    s.line(FX(-W / 2), TY(mz0), FX(W / 2), TY(mz0), w=0.2, stroke="#3d5a80", dash="1.2,0.8")
    for ix in range(H_["n_x"]):
        for iz in range(H_["n_z"]):
            x = H_["x_center"] + (ix - (H_["n_x"] - 1) / 2) * H_["pitch"]
            z = img["z"] + (iz - (H_["n_z"] - 1) / 2) * H_["pitch"]
            s.circle(FX(x), TY(z), H_["elem_d"] / 2 / k * 0.85, fill="#c7ccd3", stroke=INK2, sw=0.08)
    s.rect(FX(S.TRACKER["x"] - 40), TY(S.TRACKER["z"] - 15), 80 / k, 30 / k, fill="#2b3440", sw=0.2)
    s.circle(FX(S.ESTOP["x"]), TY(S.ESTOP["z"]), S.ESTOP["d"] / 2 / k + 0.4, fill=RED, stroke=INK, sw=0.2)
    s.line(FX(-img["width"] / 2), TY(img["z"]), FX(img["width"] / 2), TY(img["z"]), w=0.6, stroke=AQUA, dash="1,0.6")
    s.dim(FX(-W / 2), TY(-D), FX(W / 2), TY(-D), -4, f"{W:.0f}")
    s.dim(FX(W / 2), TY(-D), FX(W / 2), TY(S.LEDGE["D"]), -4, f'{D + S.LEDGE["D"]:.0f}')
    for z, t in ((S.VISOR["z_front"], "후드 앞 모서리"), (-120.0, "윗판·후드 (그 아래 미러·앞면은 숨은선)")):
        s.text(FX(-W / 2) + 1.5, TY(z) - 0.8, t, size=2.1, anchor="start", fill=INK2)
    _notes(s, 150, 112, [
        "1. 외형 초기값 (40 cm 정육면체 이내)을 넘는다: 높이 450 (받침 150, D3), 폭 480 (수평 시야, D6).",
        "2. 재질 [A]: 알루미늄 프로파일 2020 프레임, 3 mm 알루미늄 판 무광 흑색 도장, 하프미러는 아크릴 3 mm + 50:50 필름.",
        "3. 하프미러 창 모서리는 프레임에 묻고 노출 모서리는 R2 이상으로 처리한다 (SF-05).",
        "4. 레지 위: 오른쪽부터 비상정지, 햅틱 배열 (x 중심 40), 손 추적 센서 (x = -150).",
        "5. 받침 안 뒤쪽은 비워 재귀반사 시트를 바닥 20 mm 까지 내린다 (M-001).",
    ], w=40)
    return s.render(cls="dwg")


# ================================================================== S-001
def _box(s, x, y, w, h, title, sub=(), fill="#ffffff", stroke=INK, tsize=3.0):
    s.rect(x, y, w, h, fill=fill, stroke=stroke, sw=0.35, rx=1.2)
    s.text(x + 2.2, y + 4.6, title, size=tsize, weight="700")
    for i, t in enumerate(sub):
        s.text(x + 2.2, y + 8.6 + i * 3.5, t, size=2.45, fill=INK2)


def _link(s, pts, label=None, color=INK, dash=None, at=0.5, lx=0, ly=-1.2, anchor="middle", arrow="end", size=2.35):
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        last = (x2, y2) == pts[-1]
        s.line(x1, y1, x2, y2, stroke=color, w=0.35, dash=dash,
               arrow=(arrow if last else None) if arrow != "both" else ("both" if len(pts) == 2 else ("end" if last else None)))
    if label:
        i = min(int(at * (len(pts) - 1)), len(pts) - 2)
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        s.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, size=size, anchor=anchor, fill=color if color != INK else INK2)


def s001(r):
    s = _sheet("S-001", "시스템 블록도", "없음")
    _box(s, 16, 22, 70, 36, "렌더링 호스트 (기존 PC / 미니PC)",
         ["브라우저 렌더러: GLB 표시 · 버튼 상태기계", "Python 브리지: 센서 · 햅틱 · 로그", "CSV 로그 · 정렬 파일 · 설정"], tsize=2.8)
    _box(s, 118, 22, 70, 22, "고휘도 패널 7인치", ["1024×600 · 목표 ≥ 1000 cd/m² [A]", "루버 필름 반각 30° [A]"])
    _box(s, 214, 22, 70, 22, "결상 광학 (A2)", ["하프미러 50:50 + 재귀반사 시트", "차광 후드 · 무광 흑색 내장"])
    _box(s, 214, 58, 70, 14, "공중 상 154 × 86 mm", [], fill="#e9f7f1", stroke=AQUA)
    _box(s, 118, 62, 70, 18, "사용자 손 (검지 끝)", ["공중 버튼을 −z 방향으로 누른다"], fill="#fbf7ee", stroke=YELLOW)
    _box(s, 16, 66, 54, 22, "손 추적 센서", ["USB · 120 Hz [A]", "시야 140° · 30–400 mm [A]"])
    _box(s, 118, 96, 70, 32, "MCU (STM32급) [A]",
         ["위상 테이블 (버튼 5 × 64 ch)", "워치독 500 ms (SF-02)", "온도 2점 · 조도 · 상태 보고"])
    _box(s, 214, 96, 70, 22, "햅틱 드라이버 64 ch", ["MOSFET 게이트 드라이버 [A]", "12 V 레일 (릴레이 K1 뒤)"])
    _box(s, 214, 126, 70, 14, "40 kHz 배열 8 × 8 (레지 위)", [], fill="#eef4fc", stroke=BLUE)
    _box(s, 118, 142, 32, 14, "조도 센서", ["I²C · 1 Hz"])
    _box(s, 156, 142, 32, 14, "온도 × 2", ["NTC · ADC"])
    _box(s, 16, 104, 70, 20, "비상정지 S1 + 릴레이 K1", ["햅틱 전원을 MCU 와 무관하게 끊음"], stroke=RED)
    _box(s, 16, 142, 70, 20, "전원 12 V 어댑터", ["12 V: 패널 · 햅틱(K1 뒤) / 5 V: MCU", "배선과 퓨즈는 E-001"], stroke=ORANGE)
    _link(s, [(86, 33), (118, 33)], "HDMI · 60 Hz")
    _link(s, [(188, 33), (214, 33)], "빛")
    _link(s, [(249, 44), (249, 58)], "결상", lx=6, ly=1)
    _link(s, [(214, 66), (188, 69)], "보고 누름", ly=-1.6)
    _link(s, [(118, 75), (70, 75)], "적외선으로 손 관측", ly=-1.4)
    _link(s, [(40, 66), (40, 58)], "USB 손 좌표 120 Hz", lx=1.5, ly=1, anchor="start")
    _link(s, [(78, 58), (78, 90), (153, 90), (153, 96)], "USB-CDC: 출력·정지·하트비트 10 Hz ↔ 상태·온도", arrow="both", at=0.5, ly=-1.3)
    _link(s, [(188, 105), (214, 105)], "GPIO 64 ch", ly=-1.4)
    s.text(201, 111, "40 kHz · 16단 위상", size=2.2, anchor="middle", fill=INK2)
    _link(s, [(249, 118), (249, 126)], "")
    _link(s, [(134, 142), (134, 128)], "")
    _link(s, [(172, 142), (172, 128)], "")
    _link(s, [(86, 114), (100, 114), (100, 135), (204, 135), (204, 113), (214, 113)], "전원 차단 (K1)", color=RED, at=0.45, ly=-1.2)
    _link(s, [(40, 142), (40, 124)], "12 V", color=ORANGE, lx=1.5, ly=1, anchor="start")
    _link(s, [(284, 133), (289, 133), (289, 65), (284, 65)], "", color=BLUE, dash="1.4,0.8")
    s.text(249, 146, "초음파 초점이 공중 상의 버튼 위치에 맺힌다", size=2.3, anchor="middle", fill=BLUE)
    lx, ly = 96, 166
    for i, (c, t, dash) in enumerate(((INK, "데이터", None), (ORANGE, "전원", None), (RED, "안전 차단", None), (BLUE, "음향", "1.4,0.8"))):
        s.line(lx + i * 19, ly, lx + i * 19 + 6, ly, stroke=c, w=0.6, dash=dash)
        s.text(lx + i * 19 + 7.5, ly + 0.9, t, size=2.4)
    return s.render(cls="dwg")


# ================================================================== S-002
def s002(r):
    s = _sheet("S-002", "외부 기기 연결도와 API (제안)", "없음")
    s.rect(14, 20, 112, 110, stroke=INK2, sw=0.35, dash="2,1.2", rx=2)
    s.text(17, 25, "HOLO-D1 장치 경계", size=2.8, weight="700", fill=INK2)
    _box(s, 20, 30, 100, 30, "Python 브리지 (로컬 서버)",
         ["HTTP  /v1/*  ·  WebSocket  /v1/events", "토큰 인증 · 같은 LAN 만 · 속도 제한", "GLB 검사 (크기 · 폴리곤 수) 후 적용"])
    _box(s, 20, 68, 46, 22, "렌더러 (브라우저)", ["WebSocket 구독"])
    _box(s, 74, 68, 46, 22, "MCU · 햅틱", ["USB-CDC"])
    _box(s, 20, 98, 100, 24, "로컬 저장소", ["models/*.glb · layout.json · logs/*.csv", "정렬 파일 calib.json"])
    _link(s, [(43, 60), (43, 68)], "", arrow="both")
    _link(s, [(97, 60), (97, 68)], "", arrow="both")
    _link(s, [(70, 98), (70, 60)], "", arrow="both")
    ext = [
        (150, 20, "노트북 · 태블릿", ["관리 페이지: 모델 교체, 버튼 라벨, 로그 내려받기"], "Wi-Fi/LAN · HTTPS + WebSocket"),
        (150, 48, "스마트폰", ["리모컨 페이지: 재생 · 정지 · 회전"], "Wi-Fi/LAN · HTTPS"),
        (150, 76, "파트너 장비 A (네트워크)", ["버튼 이벤트 구독, 표시 내용 바꾸기"], "WebSocket /v1/events · REST"),
        (150, 104, "파트너 장비 B (키 입력만 받음)", ["MCU 가 USB HID 키보드로 버튼을 키로 보냄"], "USB HID (선택)"),
        (150, 132, "파트너 장비 C (접점 입력)", ["버튼 activate → 무전압 접점 100 ms"], "릴레이 접점 (선택)"),
    ]
    for x, y, t, sub, proto in ext:
        _box(s, x, y, 100, 24, t, sub)
        s.text(x + 2.2, y + 20, proto, size=2.4, fill=BLUE, weight="700")
        yy = y + 12
        net = "HID" not in proto and "접점" not in proto
        src, bus = ((120, 45), 133) if net else ((120, 79), 140)
        _link(s, [src, (bus, src[1]), (bus, yy), (x, yy)], None, arrow="both")
    s.text(16, 140, "API 초안 (v1, 제안 — 구현 전)", size=2.9, weight="700")
    rows = [
        ("GET  /v1/status", "상태 · 온도 · 추적 신뢰도 · 버전"),
        ("POST /v1/model", "GLB 업로드 (≤ 20 MB, 폴리곤 ≤ 10만 [A]) → 검사 후 적용"),
        ("PUT  /v1/layout", "버튼 5개 라벨 · 아이콘 · 활성 여부"),
        ("WS   /v1/events", "button {id, state, t} · tracking {conf} · safety {code}"),
        ("POST /v1/haptic/test", "관리자 전용 · 출력 상한 안에서 시험 패턴"),
    ]
    for i, (a, b) in enumerate(rows):
        s.text(18, 145.5 + i * 4.6, a, size=2.5, weight="700")
        s.text(56, 145.5 + i * 4.6, b, size=2.5, fill=INK2)
    s.text(16, 172, "보안 원칙", size=2.8, weight="700")
    s.lines(16, 176.5, ["외부에서 원격 URL 을 받아 모델을 내려받지 않는다 (업로드만).",
                         "햅틱 출력 상한은 펌웨어 고정 — API 로 넘을 수 없다 (HP-05)."], size=2.35)
    return s.render(cls="dwg")


# ================================================================== E-001
def _fuse(a):
    for v in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0):
        if v >= a:
            return v
    return a


def e001(r):
    s = _sheet("E-001", "전원 · 안전 배선도 (블록 수준)", "없음")
    P = S.POWER
    V = 12.0
    i_panel = P["7인치 고휘도 패널"][1] / V
    i_hap = P["햅틱 배열 (듀티 0.1)"][1] / V
    p5 = P["MCU·센서"][1] + P["팬"][1]
    i_5v_in = p5 / 0.9 / V                   # DC-DC 효율 0.9 [A]
    i_main = (S.POWER["7인치 고휘도 패널"][1] + S.POWER["햅틱 배열 (듀티 0.1)"][1] + p5 / 0.9) / V
    F = dict(F1=_fuse(i_main * 1.25), F2=_fuse(i_panel * 1.25), F3=_fuse(i_hap * 1.25), F4=_fuse(i_5v_in * 1.25))
    ad_w = r["power"]["psu"]
    _box(s, 14, 70, 40, 22, "AC 어댑터", [f"12 V · ≥ {ad_w:.1f} W", "(피크 × 1.3) [C]"], stroke=ORANGE)
    y12 = 81
    s.line(54, y12, 78, y12, w=0.5, stroke=ORANGE)
    s.rect(64, y12 - 2, 8, 4, fill="#fff", stroke=INK, sw=0.3)
    s.text(68, y12 - 3.2, f'F1 {F["F1"]:.1f} A', size=2.3, anchor="middle")
    s.line(78, 30, 78, 130, w=0.6, stroke=ORANGE)
    s.text(79.5, 28, "12 V 모선", size=2.6, fill=ORANGE, weight="700")
    branches = [
        (38, "F2", F["F2"], "고휘도 패널", f"피크 {S.POWER['7인치 고휘도 패널'][1]:.1f} W · {i_panel:.2f} A [C]"),
        (78, "F3", F["F3"], "햅틱 드라이버 64 ch", f"피크 {S.POWER['햅틱 배열 (듀티 0.1)'][1]:.1f} W · {i_hap:.2f} A [C]"),
        (126, "F4", F["F4"], "DC-DC 5 V (η 0.9 [A])", f"MCU·센서·팬 {p5:.1f} W · 입력 {i_5v_in:.2f} A [C]"),
    ]
    for y, fn, fv, name, sub in branches:
        s.line(78, y, 196, y, w=0.45, stroke=ORANGE)
        s.rect(88, y - 2, 8, 4, fill="#fff", stroke=INK, sw=0.3)
        s.text(92, y - 3.2, f"{fn} {fv:.1f} A", size=2.3, anchor="middle")
        _box(s, 196, y - 9, 70, 18, name, [sub])
    # 릴레이 K1 (햅틱 레일)
    kx = 140
    s.rect(kx - 6, 78 - 4, 12, 8, fill="#fff", stroke=RED, sw=0.4)
    s.text(kx, 78 + 1, "K1", size=2.6, anchor="middle", fill=RED, weight="700")
    s.text(kx, 78 + 8, "NO 접점", size=2.2, anchor="middle", fill=RED)
    # E-stop 회로
    s.line(78, 104, 112, 104, w=0.35, stroke=ORANGE)
    s.circle(116, 104, 4, fill="#fff", stroke=RED, sw=0.45)
    s.text(116, 105, "S1", size=2.5, anchor="middle", fill=RED, weight="700")
    s.text(116, 112, "비상정지 (NC, 걸림식)", size=2.3, anchor="middle", fill=RED)
    s.line(120, 104, kx, 104, w=0.35, stroke=RED)
    s.line(kx, 104, kx, 82, w=0.35, stroke=RED, dash="1,0.7")
    s.text(kx + 1.5, 95, "K1 코일 (다른 끝 GND)", size=2.3, fill=RED)
    # MCU
    _box(s, 196, 140, 70, 26, "MCU", ["EN → 드라이버 enable (워치독)", "ADC ← NTC1 패널 · NTC2 드라이버", "I²C ← 조도 센서 · USB ↔ 호스트"])
    s.line(231, 135, 231, 140, w=0.35)
    s.line(266, 153, 272, 153, w=0.35)
    s.line(272, 153, 272, 78, w=0.35, dash="1,0.7")
    s.line(272, 78, 266, 78, w=0.35, dash="1,0.7", arrow="end")
    s.text(273.5, 115, "EN", size=2.3)
    _notes(s, 14, 150, [
        "1. 비상정지 S1 은 K1 코일 회로에 직렬이다. S1 을 누르면 MCU 상태와 무관하게 햅틱 12 V 가 끊긴다 (SF-01).",
        "2. MCU 워치독: 호스트 하트비트가 500 ms 없으면 EN 을 내린다 (SF-02). 두 경로는 서로 독립이다.",
        "3. 퓨즈 값은 각 가지 피크 전류 × 1.25 를 표준값으로 올렸다 [C]. 피크 전력은 [A] 이므로 데이터시트로 다시 계산한다.",
        "4. 호스트 PC 와 손 추적 센서(USB 버스 전원)는 이 전원과 분리한다.",
        f'5. 평균 {r["power"]["avg"]:.1f} W · 피크 {r["power"]["peak"]:.1f} W · 하루 {r["power"]["wh_day"]:.0f} Wh (호스트 제외) [C].',
    ], w=64, size=2.4)
    return s.render(cls="dwg"), F


# ================================================================== E-002
def e002(r):
    s = _sheet("E-002", "햅틱 배열 배치도와 초점 기하", "1:1 · 1:2")
    H_ = S.HAPTIC
    img = r["img"]
    ox, oy = 22, 28
    s.text(ox, oy - 9, "배열 평면도 (위에서, 1:1)", size=3.0, weight="700")
    for iz in range(H_["n_z"]):
        for ix in range(H_["n_x"]):
            cx = ox + H_["elem_d"] / 2 + ix * H_["pitch"]
            cy = oy + H_["elem_d"] / 2 + iz * H_["pitch"]
            s.circle(cx, cy, H_["elem_d"] / 2, fill="#e3e7ec", stroke=INK2, sw=0.18)
            s.text(cx, cy + 0.8, f"{iz * H_['n_x'] + ix}", size=2.1, anchor="middle", fill=INK2)
        s.text(ox - 2, oy + H_["elem_d"] / 2 + iz * H_["pitch"] + 0.8, f"P{chr(65 + iz)}", size=2.2, anchor="end", fill=BLUE)
    aw = (H_["n_x"] - 1) * H_["pitch"] + H_["elem_d"]
    s.dim(ox, oy + aw, ox + aw, oy + aw, 4, f"{aw:.1f}")
    s.dim(ox + H_["elem_d"] / 2, oy, ox + H_["elem_d"] / 2 + H_["pitch"], oy, -2.5, f'피치 {H_["pitch"]:.1f}')
    s.text(ox + aw / 2, oy + aw + 10.5, "↑ 사용자 쪽 (+z)", size=2.4, anchor="middle", fill=INK2)
    # 정면 초점 기하 (x-y), 1:2
    k = 2.0
    X = lambda x: 200 + (x - H_["x_center"]) / k
    Y = lambda y: 150 - (y - H_["top_y"]) / k
    s.text(X(-40), Y(img["top"] + 30), "초점 기하 (정면, 1:2)", size=3.0, weight="700")
    s.rect(X(H_["x_center"] - aw / 2), Y(H_["top_y"]), aw / k, 7 / k, fill="#c7ccd3", sw=0.2)
    s.rect(X(-img["width"] / 2), Y(img["top"]), img["width"] / k, img["height"] / k, stroke=AQUA, sw=0.4, dash="1,0.6")
    s.text(X(-img["width"] / 2) + 1, Y(img["top"]) + 3.2, "공중 상", size=2.3, fill=AQUA)
    rows_b = []
    for i, (bx, by) in enumerate(r["buttons"]):
        dist = math.hypot(bx - H_["x_center"], by - H_["top_y"])
        ang = math.degrees(math.atan2(bx - H_["x_center"], by - H_["top_y"]))
        s.line(X(H_["x_center"]), Y(H_["top_y"]), X(bx), Y(by), stroke=BLUE, w=0.25, dash="1.2,0.7")
        s.circle(X(bx), Y(by), S.BUTTONS["d"] / 2 / k, stroke=INK, sw=0.25)
        s.text(X(bx), Y(by) + 0.8, f"{i + 1}", size=2.3, anchor="middle", weight="700")
        rows_b.append(f"버튼 {i + 1}: 거리 {dist:.0f} mm, 조향 {ang:+.1f}° [C]")
    c = r["acoustic"]["cases"]
    s.circle(X(c["center"]["peak"][0]), Y(c["center"]["peak"][1]), 0.9, fill=RED, stroke=RED)
    s.text(X(c["center"]["peak"][0]) - 1.6, Y(c["center"]["peak"][1]) + 1, "모델 최대 음압 위치 (버튼 2 조준) ", size=2.2, fill=RED, anchor="end")
    lam = r["acoustic"]["lambda_mm"]
    rows = [
        f"파장 λ = c/f = {lam:.2f} mm [C] · 피치/λ = {r['acoustic']['pitch_over_lambda']:.2f} (> 0.5 → 그레이팅 로브)",
        f"위상 16단: 한 단 = {1e6 / H_['f'] / 16:.4f} µs · 16단 양자화 손실 {c['center']['quant16_loss_db']:.2f} dB [C]",
        f"최대 조향각 {c['edge']['steer_deg']:.1f}° (버튼 배치로 제한, D5) · 그때 부엽 {c['edge']['side_db']:.1f} dB [C]",
        f"초점 음압 (버튼 2 위치) {c['center']['spl_target']:.0f} dB SPL [C, 소자 음압 [A] 기준]",
        f"채널 묶음: 행 A–H → MCU 포트 PA–PH 8비트 [A] · 미러 앞 모서리와 최소 간격 {r['clear']['min_gap_mm']:.1f} mm",
    ]
    _notes(s, 16, 132, rows, title="계산값", w=74, size=2.4)
    _notes(s, 234, 60, rows_b, title="버튼별 초점", w=30, size=2.3)
    return s.render(cls="dwg")


# ================================================================== U-001
def u001(r):
    img = r["img"]
    s = _sheet("U-001", "공중 UI 배치도 (상 평면, 1:1)", "1:1")
    cx, cy = 22 + img["width"] / 2, 40 + img["height"] / 2
    X = lambda x: cx + x
    Y = lambda y: cy - (y - img["center"][0])
    s.rect(X(-img["width"] / 2), Y(img["top"]), img["width"], img["height"], fill="#0b0d10", stroke=AQUA, sw=0.4)
    s.text(X(-img["width"] / 2), Y(img["top"]) - 2.5, f'공중 상 전체 {img["width"]:.1f} × {img["height"]:.1f} mm — 검정 = 빛 없음 = 공기 (투명)', size=2.6)
    mb = S.MODEL_BOX
    s.rect(X(mb["x0"]), Y(img["center"][0] + mb["y1"]), mb["x1"] - mb["x0"], mb["y1"] - mb["y0"], stroke="#6da7ec", sw=0.3, dash="1,0.7")
    s.text(X((mb["x0"] + mb["x1"]) / 2), Y(img["center"][0]) + 1, "3D 모델 영역", size=3.0, anchor="middle", fill="#9ec5f4")
    for i, (bx, by) in enumerate(r["buttons"]):
        s.circle(X(bx), Y(by), S.FSM["R_hover"], stroke="#55606c", sw=0.2, dash="0.8,0.8")
        s.circle(X(bx), Y(by), S.BUTTONS["d"] / 2, fill="#1b2129", stroke="#e8ecf0", sw=0.5)
        s.text(X(bx), Y(by) + 1.1, S.BUTTONS["labels"][i], size=3.0, anchor="middle", fill="#ffffff", weight="700")
    H_ = S.HAPTIC
    aw = (H_["n_x"] - 1) * H_["pitch"] + H_["elem_d"]
    s.rect(X(H_["x_center"] - aw / 2), Y(img["bottom"]) + 6, aw, 4, fill="#c7ccd3", stroke=INK2, sw=0.2)
    s.text(X(H_["x_center"]), Y(img["bottom"]) + 15, "아래 햅틱 배열의 x 범위 (레지 위)", size=2.4, anchor="middle", fill=INK2)
    s.line(X(0), Y(img["top"]) - 0.5, X(0), Y(img["bottom"]) + 0.5, stroke="#3b4652", w=0.15, dash="0.6,0.6")
    s.line(X(-img["width"] / 2) - 0.5, Y(img["center"][0]), X(img["width"] / 2) + 0.5, Y(img["center"][0]), stroke="#3b4652", w=0.15, dash="0.6,0.6")
    b0 = r["buttons"]
    s.dim(X(b0[0][0]), Y(b0[0][1]) - S.BUTTONS["d"] / 2, X(b0[1][0]), Y(b0[1][1]) - S.BUTTONS["d"] / 2, -3.5, f'{b0[1][0] - b0[0][0]:.0f}', color="#c3c9d1")
    s.dim(X(b0[3][0]) - S.BUTTONS["d"] / 2, Y(b0[3][1]) + S.BUTTONS["d"] / 2, X(b0[3][0]) + S.BUTTONS["d"] / 2, Y(b0[3][1]) + S.BUTTONS["d"] / 2, 3.5, f'⌀{S.BUTTONS["d"]:.0f}', color="#c3c9d1")
    bl = r["blur"]
    rows = [f"버튼 {i + 1} '{S.BUTTONS['labels'][i]}': x {bx:+.0f}, 상 중심에서 y {by - img['center'][0]:+.0f} mm" for i, (bx, by) in enumerate(b0)]
    rows += [
        f"점선 원 = hover 반경 R_hover {S.FSM['R_hover']:.0f} mm [A]. 겹치면 가장 가까운 버튼만 처리한다.",
        f"상 흐림 지름 (프리즘 시트) {bl['prism']:.1f} mm [C] → 글자·아이콘 획 굵기 ≥ {bl['prism'] / 2:.1f} mm, 글자 높이 ≥ {2 * bl['prism']:.0f} mm 권장.",
        "누르는 방향 = 사용자에서 장치 쪽 (−z). 누름 깊이 10 mm 에서 activate, 5 mm 로 돌아오면 해제.",
        "3D 모델은 버튼과 겹치지 않는 왼쪽 영역에만 그린다 (버튼 위 오입력 방지).",
    ]
    _notes(s, 190, 30, rows, title="배치 규칙", w=40, size=2.4)
    return s.render(cls="dwg")


def all_drawings(r):
    e1, fuses = e001(r)
    return dict(M001=m001(r), M002=m002(r), S001=s001(r), S002=s002(r), E001=e1, E002=e002(r), U001=u001(r)), fuses
