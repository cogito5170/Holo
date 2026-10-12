"""HOLO-D1 계산 모델. 입력은 spec.py 뿐이고, 결과는 dict 로 돌려준다 (그림·보고서가 이 값을 읽는다).

모든 출력은 [A] 가정 파라미터 위의 모델 계산 [C] 이다. 실측 [M] 이 아니다.
"""
import math

import numpy as np

from blueprint import spec as S


# ================================================================== 1. 광학: 면대칭 결상
def _vec(y, z):
    return np.array([y, z], dtype=float)


def reflect_point(p):
    """미러 평면에 대한 점 p(y,z)의 대칭점. 면대칭 결상의 정의식."""
    (y0, z0), _ = S.mirror_endpoints()
    n = _vec(*S.mirror_normal())
    m = _vec(y0, z0)
    p = np.asarray(p, float)
    return p - 2 * np.dot(p - m, n) * n


def reflect_dir(d):
    n = _vec(*S.mirror_normal())
    d = np.asarray(d, float)
    return d - 2 * np.dot(d, n) * n


def hit_mirror(p, d):
    """점 p 에서 방향 d 로 가는 직선과 미러 직선의 교점 (y,z) 과 매개변수 t."""
    (y0, z0), _ = S.mirror_endpoints()
    n = _vec(*S.mirror_normal())
    t = np.dot(_vec(y0, z0) - p, n) / np.dot(d, n)
    return p + t * d, t


def on_mirror(q, tol=1e-9):
    (y0, z0), (y1, z1) = S.mirror_endpoints()
    return min(y0, y1) - tol <= q[0] <= max(y0, y1) + tol and min(z0, z1) - tol <= q[1] <= max(z0, z1) + tol


def trace_two_rays(p, ang_deg=(-8.0, 8.0)):
    """독립 검사: 패널 점 p 에서 각도가 다른 두 광선을 미러→재귀반사→미러 투과로 추적해 두 귀환 광선의 교점을 구한다.

    이상적 재귀반사(정확히 되돌림)를 가정한다. 교점이 reflect_point(p) 와 같아야 한다.
    """
    lines = []
    for a in ang_deg:
        a = math.radians(a)
        d = _vec(math.cos(a), math.sin(a))              # 거의 위(+y)로, z 로 조금 기운 광선
        h, _ = hit_mirror(np.asarray(p, float), d)
        d2 = reflect_dir(d)                              # 미러 반사 후 뒤(-z) 쪽으로
        t = (S.RETRO["z"] - h[1]) / d2[1]
        q = h + t * d2                                   # 재귀반사 시트 위 점
        back = -d2                                       # 되돌림
        h2, _ = hit_mirror(q, back)                      # 미러에 다시 도달 (= h)
        lines.append((h2, back))                         # 투과 후 같은 방향으로 계속
    (p1, d1), (p2, d2) = lines
    A = np.column_stack([d1, -d2])
    s = np.linalg.solve(A, p2 - p1)
    return p1 + s[0] * d1, lines


def image_geometry():
    z0, z1 = S.panel_z_range()
    py = S.PANEL["y"]
    pc = _vec(py, S.PANEL["z_center"])
    ic = reflect_point(pc)
    i_a = reflect_point(_vec(py, z0))                    # 패널 뒤쪽 가장자리의 상
    i_b = reflect_point(_vec(py, z1))                    # 패널 앞쪽 가장자리의 상
    traced, _ = trace_two_rays(pc)
    (my0, mz0), _ = S.mirror_endpoints()
    d_panel = abs(np.dot(pc - _vec(my0, mz0), _vec(*S.mirror_normal())))
    d_image = abs(np.dot(ic - _vec(my0, mz0), _vec(*S.mirror_normal())))
    return dict(
        center=ic, top=max(i_a[0], i_b[0]), bottom=min(i_a[0], i_b[0]), z=float(ic[1]),
        width=S.PANEL["size_x"], height=abs(i_a[0] - i_b[0]),
        diag=math.hypot(S.PANEL["size_x"], abs(i_a[0] - i_b[0])),
        front_edge_maps_to="bottom" if i_b[0] < i_a[0] else "top",
        trace_err=float(np.linalg.norm(traced - ic)),
        d_panel=d_panel, d_image=d_image,
        z_ok=0.0 < ic[1] < S.LEDGE["D"],
    )


# ------------------------------------------------------------------ 시청 영역
def _visible(eye, img_pts):
    """eye=(x,y,z). img_pts: (x,y,z) 배열. 모든 점에서 (1) 미러 통과점이 미러 안 (2) 재귀반사 점이 시트 안 (3) 시선이 후드에 안 막힘."""
    (my0, mz0), (my1, mz1) = S.mirror_endpoints()
    n = np.array([0.0, *S.mirror_normal()])             # (x, y, z)
    m = np.array([0.0, my0, mz0])
    half_w = S.MIRROR["width"] / 2
    for ip in img_pts:
        d = ip - eye                                      # 눈 → 상, 그 너머로 연장
        t = np.dot(m - ip, n) / np.dot(d, n)
        if t <= 0:
            return False
        h = ip + t * d
        if not (abs(h[0]) <= half_w and min(my0, my1) <= h[1] <= max(my0, my1)):
            return False
        t2 = (S.RETRO["z"] - h[2]) / d[2]
        q = h + t2 * d
        if not (abs(q[0]) <= half_w and S.RETRO["y0"] <= q[1] <= S.RETRO["y1"]):
            return False
        # 미러→재귀반사 구간이 패널(두께 10 mm 가정)을 지나는가
        if d[1] != 0:
            pz0, pz1 = S.panel_z_range()
            for yy in (S.PANEL["y"], S.PANEL["y"] - 10.0):
                tp = (yy - h[1]) / d[1]
                if 0 < tp < t2:
                    pp = h + tp * d
                    if pz0 <= pp[2] <= pz1 and abs(pp[0]) <= S.PANEL["size_x"] / 2 + 10:
                        return False
        # 후드 윗판(y = VISOR.y, z <= VISOR.z_front) 이 상→눈 구간을 가리는가
        if d[1] != 0:
            tv = (S.VISOR["y"] - ip[1]) / d[1]
            if 0 < tv < 1:
                pv = ip + tv * d
                if pv[2] <= S.VISOR["z_front"]:
                    return False
    return True


def viewing_zone(img):
    xs = np.linspace(-img["width"] / 2, img["width"] / 2, 7)
    ys = np.linspace(img["bottom"], img["top"], 5)
    pts = np.array([[x, y, img["z"]] for x in xs for y in ys])
    ex, ey, ez = 0.0, S.VIEWER["eye_y"], S.VIEWER["eye_z"]
    nominal = _visible(np.array([ex, ey, ez]), pts)
    c = np.array([0.0, img["center"][0], img["z"]])
    # 수평: 같은 거리(상 중심에서 eye 까지)의 원 위에서 각도를 늘려 간다
    r = math.hypot(ey - c[1], ez - c[2])
    elev = math.atan2(ey - c[1], ez - c[2])
    def eye_at(az, el):
        return c + r * np.array([math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el)])
    h_lim = 0.0
    for a in np.arange(0, 60.01, 0.25):
        if _visible(eye_at(math.radians(a), elev), pts):
            h_lim = a
        else:
            break
    v_lo, v_hi = None, None
    for e in np.arange(-30, 80.01, 0.25):
        ok = _visible(eye_at(0.0, math.radians(e)), pts)
        if ok and v_lo is None:
            v_lo = e
        if ok:
            v_hi = e
    # 눈 높이 범위 (eye_z 고정)
    y_ok = [y for y in np.arange(150, 800, 2.0) if _visible(np.array([0.0, y, ez]), pts)]
    return dict(nominal=nominal, h_half_deg=h_lim, elev_deg=math.degrees(elev),
                v_range_deg=(v_lo, v_hi), eye_y_range=(min(y_ok), max(y_ok)) if y_ok else None, r=r)


def array_clear(img):
    """초음파 경로 검사: 모든 소자 → 모든 버튼 초점 선분이 하프미러 선분을 가로지르지 않는가."""
    (my0, mz0), (my1, mz1) = S.mirror_endpoints()
    worst = None
    for e in elements(img) * 1e3:
        for bx, by in button_points(img):
            a = np.array([e[1], e[2]])
            b = np.array([by, img["z"]])
            # 두 선분 (a,b) 와 (m0,m1) 의 교차 (y,z 평면; x 는 미러 폭 안이라고 본다)
            m0, m1 = np.array([my0, mz0]), np.array([my1, mz1])
            A = np.column_stack([b - a, m0 - m1])
            if abs(np.linalg.det(A)) < 1e-12:
                continue
            s_, u = np.linalg.solve(A, m0 - a)
            if 0 <= s_ <= 1 and 0 <= u <= 1:
                return dict(clear=False, hit=(float(a[0]), float(a[1])))
            # 여유: 경로가 미러 앞 모서리 아래를 지나는 거리
            g = (a + s_ * (b - a)) if 0 <= s_ <= 1 else None
            if g is not None and u < 0:
                d = float(np.linalg.norm(g - m0))
                worst = d if worst is None else min(worst, d)
    return dict(clear=True, min_gap_mm=worst)


def panel_angles(img):
    """(1) 기준 시선의 공중 상 광선이 패널에서 나올 때 패널 법선과 이루는 각 — 루버가 통과시켜야 하는 각
    (2) 기준 눈에서 하프미러를 투과해 패널을 직접 볼 때의 각 — 루버가 막아야 하는 각."""
    eye = np.array([S.VIEWER["eye_y"], S.VIEWER["eye_z"]])
    need = []
    for y in np.linspace(img["bottom"], img["top"], 9):
        ip = np.array([y, img["z"]])
        d = ip - eye                                     # 눈→상, 연장하면 미러로
        h, _ = hit_mirror(ip, d)
        p = reflect_point(ip)                            # 그 광선은 패널 점 p 에서 왔다 (미러 반사 경로)
        v = h - p
        need.append(abs(math.degrees(math.atan2(v[1], v[0]))))   # 패널 법선 = +y
    zs = np.linspace(*S.panel_z_range(), 9)
    direct = [abs(math.degrees(math.atan2(eye[1] - z, eye[0] - S.PANEL["y"]))) for z in zs]
    return dict(emit_max=max(need), direct_min=min(direct), louver=S.PANEL["louver_half_deg"],
                ok=max(need) < S.PANEL["louver_half_deg"] < min(direct))


def blur(img):
    """재귀반사 퍼짐에 의한 상 흐림 지름 ≈ 2·d·tan(δ). d = 상 중심 → 재귀반사 시트 경로 길이 (기준 시선)."""
    eye = np.array([0.0, S.VIEWER["eye_y"], S.VIEWER["eye_z"]])
    ip = np.array([0.0, img["center"][0], img["z"]])
    d = ip - eye
    (my0, mz0), _ = S.mirror_endpoints()
    n = np.array([0.0, *S.mirror_normal()])
    t = np.dot(np.array([0.0, my0, mz0]) - ip, n) / np.dot(d, n)
    h = ip + t * d
    q = h + (S.RETRO["z"] - h[2]) / d[2] * d
    L = float(np.linalg.norm(q - ip))
    px = S.PANEL["size_x"] / S.PANEL["px_x"]
    return dict(path_mm=L, pixel_mm=px,
                **{k: 2 * L * math.tan(math.radians(v)) for k, v in S.RETRO["div_deg"].items()})


# ------------------------------------------------------------------ 주변광 대비
def background_luminance(hood):
    a = S.AMBIENT
    if hood:
        L_above = a["rho_black"] * a["hood_E_frac"] * a["E_room"] / math.pi
    else:
        L_above = a["rho_room"] * a["E_room"] / math.pi
    L_behind = a["rho_retro_dark"] * a["interior_E_frac"] * a["E_room"] / math.pi
    return S.MIRROR["R"] * L_above + S.MIRROR["T"] * L_behind, S.MIRROR["R"] * L_above, S.MIRROR["T"] * L_behind


def efficiency(sheet):
    return S.MIRROR["R"] * S.MIRROR["T"] * S.RETRO["eta"][sheet]


def contrast(L_panel, sheet, hood):
    L_bg = background_luminance(hood)[0]
    return (efficiency(sheet) * L_panel + L_bg) / L_bg


def required_panel(sheet, hood, C=3.0):
    """닫힌 식: C = (η L + B)/B  →  L = (C-1) B / η."""
    return (C - 1) * background_luminance(hood)[0] / efficiency(sheet)


def required_panel_numeric(sheet, hood, C=3.0):
    lo, hi = 0.0, 1e6
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if contrast(mid, sheet, hood) < C else (lo, mid)
    return (lo + hi) / 2


def contrast_table():
    rows = []
    for sheet in ("prism", "bead"):
        for hood in (True, False):
            B, B_ref, B_beh = background_luminance(hood)
            rows.append(dict(sheet=sheet, hood=hood, eff=efficiency(sheet), L_bg=B, L_bg_reflect=B_ref, L_bg_behind=B_beh,
                             C_at_max=contrast(S.PANEL["L_max"], sheet, hood),
                             L_req=required_panel(sheet, hood), L_req_num=required_panel_numeric(sheet, hood)))
    return rows


# ================================================================== 2. 햅틱: 40 kHz 위상배열 음장
def _j1(x):
    """1차 베셀 함수 J1 (급수, |x| < 10 에서 충분). scipy 없이 계산한다."""
    x = np.asarray(x, float)
    out = np.zeros_like(x)
    term = x / 2
    out += term
    for k in range(1, 30):
        term = term * (-(x / 2) ** 2) / (k * (k + 1))
        out += term
    return out


def directivity(theta):
    H = S.HAPTIC
    ka = 2 * math.pi * H["f"] / H["c"] * (H["elem_d"] / 2e3)
    s = ka * np.sin(theta)
    with np.errstate(invalid="ignore", divide="ignore"):
        D = np.where(np.abs(s) < 1e-9, 1.0, 2 * _j1(s) / s)
    return D


def elements(img):
    H = S.HAPTIC
    xs = (np.arange(H["n_x"]) - (H["n_x"] - 1) / 2) * H["pitch"] + H["x_center"]
    zs = (np.arange(H["n_z"]) - (H["n_z"] - 1) / 2) * H["pitch"] + img["z"]
    return np.array([[x, H["top_y"], z] for z in zs for x in xs]) / 1e3      # m


def button_points(img):
    """버튼 중심 (x, y) — 공중 상 평면(z = img.z) 위."""
    return [(float(x), float(img["center"][0] + dy)) for dy, xs in S.BUTTONS["rows"] for x in xs]


def field(points_m, el, focus_m, phase_steps=None):
    """복소 음압(rms 진폭, Pa). points_m: (N,3) m."""
    H = S.HAPTIC
    k = 2 * math.pi * H["f"] / H["c"]
    phi = k * np.linalg.norm(el - focus_m, axis=1)
    if phase_steps:
        q = 2 * math.pi / phase_steps
        phi = np.round(phi / q) * q
    p = np.zeros(len(points_m), complex)
    for e, ph in zip(el, phi):
        r_vec = points_m - e
        r = np.linalg.norm(r_vec, axis=1)
        cos_t = np.clip(r_vec[:, 1] / r, -1, 1)            # 소자 축 = +y
        D = directivity(np.arccos(cos_t))
        p += H["p0_rms"] * H["r0"] / r * D * np.exp(1j * (k * r - ph))
    return p


def spl(p_rms):
    return 20 * np.log10(np.maximum(np.abs(p_rms), 1e-12) / 20e-6)


def _run_width(v, i, g, thr):
    """index i 를 포함하는 thr 이상 연속 구간의 폭."""
    lo = i
    while lo > 0 and v[lo - 1] >= thr:
        lo -= 1
    hi = i
    while hi < len(v) - 1 and v[hi + 1] >= thr:
        hi += 1
    return float(g[hi] - g[lo])


def acoustic(img, step_mm=1.0):
    H = S.HAPTIC
    el = elements(img)
    btn = button_points(img)
    out = dict(lambda_mm=H["c"] / H["f"] * 1e3, pitch_over_lambda=H["pitch"] / (H["c"] / H["f"] * 1e3), cases={})
    xg = np.arange(-60, 140 + 1e-9, step_mm)
    yg = np.arange(H["top_y"] + 15, img["top"] + 30 + 1e-9, step_mm)
    X, Y = np.meshgrid(xg, yg)
    P = np.column_stack([X.ravel(), Y.ravel(), np.full(X.size, img["z"])]) / 1e3
    edge = max(btn, key=lambda b: math.atan2(abs(b[0] - H["x_center"]), b[1] - H["top_y"]))
    for name, (bx, by) in (("center", btn[1]), ("edge", edge)):
        f = np.array([bx, by, img["z"]]) / 1e3
        pf = field(P, el, f)
        amp = np.abs(pf).reshape(X.shape)
        i = np.unravel_index(np.argmax(amp), amp.shape)
        peak_xy = (float(X[i]), float(Y[i]))
        p_peak = float(amp[i])
        # 수평(x) 반폭: 초점 높이의 행
        fwhm_x = _run_width(amp[i[0], :], i[1], xg, p_peak / 2)
        fwhm_y = _run_width(amp[:, i[1]], i[0], yg, p_peak / 2)
        # 초점 밖 최대 (부엽/그레이팅 로브): 초점에서 2·FWHM 밖
        mask = (np.hypot(X - peak_xy[0], (Y - peak_xy[1]) * fwhm_x / max(fwhm_y, 1e-9)) > fwhm_x * 1.5)
        side = float(amp[mask].max()) if mask.any() else 0.0
        focus_dist = float(np.linalg.norm(f - el.mean(axis=0)) * 1e3)
        steer = math.degrees(math.atan2(abs(bx - H["x_center"]), by - H["top_y"]))
        # 방사압 (완전 반사 평면파 근사): P_rad ≈ 2 p_rms² / (ρ c²);  힘 ≈ P_rad × 초점 면적(π (FWHM/2)²)
        p_rad = 2 * p_peak ** 2 / (H["rho_air"] * H["c"] ** 2)
        area = math.pi * (fwhm_x / 2e3) ** 2
        # 위상 16단 양자화 손실
        p_target = abs(field(f[None, :], el, f)[0])
        pq = abs(field(f[None, :], el, f, phase_steps=16)[0])
        pe = abs(field(f[None, :], el, f)[0])
        ear = np.array([[0.0, S.VIEWER["eye_y"], S.VIEWER["eye_z"]]]) / 1e3
        p_ear = abs(field(ear, el, f)[0])
        out["cases"][name] = dict(
            focus=(bx, by), peak=peak_xy, peak_err=math.hypot(peak_xy[0] - bx, peak_xy[1] - by),
            p_peak=p_peak, spl_peak=float(spl(p_peak)), p_target=float(p_target), spl_target=float(spl(p_target)), fwhm_x=fwhm_x, fwhm_y=fwhm_y,
            side_db=float(20 * math.log10(side / p_peak)) if side > 0 else -99.0,
            focus_dist=focus_dist, steer_deg=steer, p_rad=p_rad, force_mN=p_rad * area * 1e3,
            quant16_loss_db=float(20 * math.log10(pq / pe)), spl_ear=float(spl(p_ear)),
            grid=(xg, yg, amp))
    return out


def acoustic_convergence(img):
    """격자 간격 2 mm vs 0.5 mm 의 초점 최대 음압·반폭 차 (수렴 검사)."""
    a = acoustic(img, 2.0)["cases"]["center"]
    b = acoustic(img, 0.5)["cases"]["center"]
    return dict(p2=a["p_peak"], p05=b["p_peak"], rel=abs(a["p_peak"] - b["p_peak"]) / b["p_peak"],
                fwhm2=a["fwhm_x"], fwhm05=b["fwhm_x"])


# ================================================================== 3. 지연·전력
def latency(acc):
    t_fly = acc["cases"]["center"]["focus_dist"] / 1e3 / S.HAPTIC["c"] * 1e3
    hap = [(n, t_fly if v is None else v) for n, v in S.LAT_HAPTIC]
    vis = list(S.LAT_VISUAL)
    after_act = sum(v for n, v in hap[3:])
    return dict(visual=vis, haptic=hap, visual_total=sum(v for _, v in vis), haptic_total=sum(v for _, v in hap),
                haptic_after_activate=after_act, t_fly=t_fly)


def power():
    avg = sum(a for a, _ in S.POWER.values())
    peak = sum(p for _, p in S.POWER.values())
    return dict(avg=avg, peak=peak, psu=peak * (1 + S.PSU_MARGIN), wh_day=avg * 24)


def width_sweep(img, widths=(360, 400, 440, 480, 520)):
    keep = S.MIRROR["width"]
    out = []
    for W in widths:
        S.MIRROR["width"] = W - 2 * S.BODY["wall"]
        out.append((W, viewing_zone(img)["h_half_deg"]))
    S.MIRROR["width"] = keep
    return out


def run():
    img = image_geometry()
    acc = acoustic(img)
    return dict(img=img, view=viewing_zone(img), blur=blur(img), contrast=contrast_table(),
                clear=array_clear(img), angles=panel_angles(img), sweep=width_sweep(img),
                acoustic=acc, conv=acoustic_convergence(img), lat=latency(acc), power=power(),
                buttons=button_points(img), D0=float(directivity(np.array([0.0]))[0]))


if __name__ == "__main__":
    r = run()
    i = r["img"]
    print("image center (y,z)", i["center"], "size", i["width"], i["height"], "diag", round(i["diag"], 1), "trace err", i["trace_err"])
    print("view", {k: v for k, v in r["view"].items()})
    print("blur", r["blur"]); print("clear", r["clear"], "angles", r["angles"])
    for c in r["contrast"]:
        print(c)
    for k, c in r["acoustic"]["cases"].items():
        print(k, {kk: (round(v, 3) if isinstance(v, float) else v) for kk, v in c.items() if kk != "grid"})
    print("conv", r["conv"], "lat", r["lat"]["visual_total"], r["lat"]["haptic_total"], r["lat"]["haptic_after_activate"], "power", r["power"])
