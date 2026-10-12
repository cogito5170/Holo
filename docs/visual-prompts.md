# 완성 모습 이미지 생성 프롬프트

- 목적: 1차 프로토타입(`docs/spec.md` v0.1)이 완성됐을 때의 모습을, 이미지 생성 모델로 **가능한 한 사양에 가깝게** 뽑기 위한 프롬프트 모음이다.
- 작성일: 2026-10-12

> **표기 규칙.** 이 프롬프트로 만든 이미지는 **컨셉 렌더**다. 제품 사진이나 실측 결과가 아니다.
> 보고서나 발표에 쓸 때는 캡션에 `컨셉 이미지 — 생성 모델 출력, 실물 아님`을 반드시 붙인다.
> 치수와 도면은 이미지 모델이 지키지 못하므로, 정확한 도면은 사양 파일에서 계산한 그림을 쓴다.

---

## 0. 왜 프롬프트를 이렇게 쓰는가

이미지 모델에게 "hologram display"라고만 쓰면 거의 항상 **SF식 홀로그램**이 나온다. 파란 빛기둥, 바닥에서 쏘는 원뿔형 빔, 반투명 유령 같은 사람 따위다. 이 프로젝트의 실제 모습과는 전혀 다르다.

실제 장치는 다음과 같다.

1. **무광 검정 상자 + 앞쪽 어두운 유리창.** 이 창이 45° 하프미러다. 빛줄기는 보이지 않는다.
2. **공중 상은 평평하다.** 화면을 공중에 옮겨 놓은 것이라 입체감은 음영과 회전에서 나온다. 화면보다 **약간 어둡고**, 정면 ±15° 안에서만 보인다.
3. 상은 유리창 **앞쪽 허공**에 떠 있다. 손가락이 그 위치에 닿는다.
4. 상 아래 받침대(레지)에 **초음파 트랜스듀서 격자(8×8, 은색 원통)**가 위를 향해 있다. 그 옆에 **손추적 센서 바**가 있다.
5. 밝은 사무실(약 500 lux)에서 쓴다. 어두운 무대가 아니다.

그래서 모든 프롬프트는 공통 블록(§1)으로 형태를 고정하고, 금지 목록(§2)으로 SF 클리셰를 막는다.

---

## 1. 공통 블록 (모든 프롬프트 앞에 붙인다)

```text
A compact desktop "aerial display" prototype, about 36 cm wide, 30 cm tall and 40 cm deep, sitting on an office desk.
Matte black powder-coated aluminium enclosure with soft 3 mm rounded edges and a black anodised aluminium extrusion frame.
The front face is a large dark half-mirror window (smoked-glass look) tilted back about 45 degrees; through it you can only faintly see a dark interior.
Floating in mid-air about 8 cm in front of the window is a crisp, flat, bright image (about 10 cm diagonal) of a slowly rotating 3D object,
rendered with soft studio shading so it reads as 3D, slightly dimmer than a phone screen, with no frame, no beam of light and no glow cone.
Below the floating image, a shallow front ledge (10 cm deep) holds an 8 x 8 grid of small silver ultrasonic transducers (10 mm cylinders, black mesh tops) facing straight up,
and a slim black hand-tracking sensor bar with two small dark lenses. A small red latching emergency-stop button sits on the right corner of the ledge.
Five small translucent circular buttons float in a shallow arc just below the 3D object, at the same depth as the floating image.
Bright, realistic office lighting, neutral white balance, soft shadows on the desk.
```

**한국어 요약:** 사무실 책상 위의 무광 검정 상자(약 36×30×40 cm)다. 앞면에 45° 기운 어두운 유리창이 있다. 창 앞 약 8 cm 허공에 대각 10 cm의 평평하고 선명한 3D 물체 상이 떠 있다. 그 아래 받침대에 은색 초음파 소자 8×8 격자(위를 향함), 손추적 센서 바, 빨간 비상정지 버튼이 있다. 상 아래에는 반투명 원형 버튼 5개가 호를 그리며 떠 있다. 밝은 사무실 조명이다.

> 치수는 `docs/spec.md`의 초기값(외형 40 cm 이내, 상 대각 ≥ 100 mm, 햅틱 8×8)에서 가져왔다. 사양이 바뀌면 이 블록부터 고친다.

---

## 2. 금지 목록 (negative prompt / "피할 것")

```text
sci-fi hologram, blue light beam, cone of light, projector rays, volumetric fog, laser beams, glowing particles,
transparent ghost person, Iron Man style UI, neon cyberpunk, dark stage, spotlight, lens flare, rainbow speckle,
floating image without a device, image inside the glass, curved screen, VR headset, smartphone hologram pyramid,
text, watermark, logo, brand names, distorted fingers, extra fingers
```

- Stable Diffusion / Flux: 위 목록을 negative prompt 칸에 넣는다.
- 네거티브 칸이 없는 도구(Midjourney, GPT 이미지, Gemini/Imagen 등): 프롬프트 끝에 이렇게 붙인다.
  - `Avoid: sci-fi hologram beams, light cones, neon, dark stage, text, logos.`
  - Midjourney는 `--no beam, cone of light, neon, text, logo`로 쓴다.

---

## 3. 장면별 프롬프트

모든 장면은 **[공통 블록] + 장면 문장 + [금지 목록]**으로 조립한다. 장면 문장만 아래에 적었다.

### P1. 제품 대표컷 (3/4 정면)

```text
Product photograph, three-quarter front view from slightly above, 50 mm lens, f/5.6, shallow depth of field on the floating image.
The floating object is a small glossy wireless earbud case, rotating, with a soft reflection-free look.
The five floating buttons are labelled only with simple icons (play, pause, rotate, zoom in, zoom out), pale white with thin outlines.
Clean minimal desk, a closed laptop in the blurred background.
```
- 비율: `--ar 3:2` (가로)
- 볼 것: 상이 **유리창 앞**에 있는지, 빛줄기가 없는지, 받침대에 소자 격자가 있는지.

### P2. 사용 장면 (사람이 버튼을 누름)

```text
Lifestyle photograph, side-front view at seated eye level. A person (face out of frame, only shoulder, forearm and hand visible)
sits at the desk and gently touches one of the floating buttons with the tip of the index finger.
The fingertip is exactly at the depth of the floating image; the touched button is highlighted with a thin bright ring.
The person's hand is about 15 cm above the transducer grid. Natural office daylight from a window on the left.
```
- 비율: `--ar 16:9`
- 볼 것: 손가락이 상과 **같은 깊이**에 있는지, 손가락 개수가 정상인지, 얼굴이 나오지 않는지 (초상권 문제 회피).

### P3. 상호작용 접사 (손끝 + 햅틱 소자)

```text
Macro close-up, 85 mm lens, eye level with the floating button.
The fingertip presses into a floating circular button; the button shows a subtle ripple ring to indicate a click.
Directly below, the 8 x 8 silver ultrasonic transducer grid on the ledge is in soft focus.
A faint, almost invisible shimmer in the air above the grid suggests focused ultrasound; no visible beam.
```
- 비율: `--ar 4:5`
- 볼 것: 초음파는 **보이지 않는 것**이 사실이다. 빔이나 빛줄기가 그려졌으면 다시 뽑는다.

### P4. 단면 설명도 (광학 경로) — 기술 일러스트

```text
Clean technical cutaway illustration, side section view, flat vector style with thin lines, white background.
Inside the black enclosure: a bright display panel lies flat at the bottom facing up; above it a half-mirror sheet is tilted at 45 degrees;
a retroreflective sheet stands vertically at the back wall facing the mirror.
Thin orange arrows show light going up from the panel, reflecting off the half-mirror toward the back retroreflector,
returning along the same path, passing through the half-mirror and converging into a floating image in front of the window.
A dashed line marks the mirror plane; the panel and the floating image are drawn at equal distances on either side of it (plane symmetry).
Below the floating image, the ultrasonic transducer grid on the ledge sends faint blue converging wavefronts to a focal point at the fingertip.
Minimal Korean labels: 패널, 하프미러, 재귀반사 시트, 공중 상, 초음파 초점.
```
- 비율: `--ar 3:2`
- 주의: 한글 라벨은 대부분의 모델이 깨뜨린다. 라벨 없이 뽑고 나중에 직접 넣는 것을 권한다 (프롬프트에서 마지막 줄 삭제).
- 이 그림은 **설명용**이다. 정식 단면도는 사양 파일에서 계산해 그린다.

### P5. 분해도 (제품 디자인 스타일)

```text
Exploded axonometric view of the prototype on a light grey background, product-design presentation style, soft shadows.
Layers separated vertically and labelled with thin leader lines: black enclosure shell,
45-degree half-mirror front window, vertical retroreflective sheet, 10-inch high-brightness display panel, matte black light-absorbing liner,
front ledge with 8 x 8 ultrasonic transducer board and its driver board, hand-tracking sensor bar,
microcontroller board, ambient light sensor, emergency-stop button, DC power adapter.
```
- 비율: `--ar 4:5` 또는 `--ar 1:1`

### P6. 청사진 스타일 (블루프린트 시트)

```text
Engineering blueprint sheet, white line art on deep Prussian blue paper, subtle paper grain.
Orthographic three views (front, side section, top) of the desktop aerial display with dimension lines and arrowheads,
a section showing the 45-degree half-mirror and the floating image position, an 8 x 8 grid detail in a circle callout,
and a title block in the lower right corner. Precise, minimal, drafting-style lettering; no real brand names.
```
- 비율: `--ar 297:210` (A4 가로)
- 주의: 생성 모델의 치수 숫자는 **믿을 수 없다**. 분위기용 표지·간지로만 쓴다. 실제 수치가 들어간 도면은 사양 파일에서 계산해 만든다 (청사진 정책: 그림에 숫자를 손으로 쓰지 않는다).

### P7. UI 상태 시트 (공중 버튼 6상태)

```text
UI design sheet on a dark charcoal background, six panels in a 3 x 2 grid, each showing the same floating circular button (flat, minimal, soft glow edge):
1 idle - thin grey outline; 2 hover - brighter outline and slightly larger; 3 arm - outline fills halfway like a progress ring;
4 activate - solid white fill with a ripple ring; 5 tracking lost - dashed amber outline with a small hand-slash icon;
6 safety stop - solid red ring with a stop icon.
Below each panel, small caption text slots (leave blank). Clean, high-contrast, readable at arm's length.
```
- 비율: `--ar 3:2`
- 상태 정의는 `docs/spec.md` 5.4의 상태기계와 같다. 색상 규칙은 회색 → 흰색 → 앰버(경고) → 빨강(정지)이다.

### P8. 연결 구성도 (아이소메트릭 인포그래픽)

```text
Isometric infographic on a white background. The black desktop aerial display in the centre, connected by thin labelled cables:
USB to a small fanless mini PC (host), HDMI from the mini PC to the display, USB from the mini PC to the hand-tracking bar,
USB serial from the mini PC to a small microcontroller board that drives the ultrasonic grid,
a wireless link icon from the mini PC to a laptop and a smartphone showing a simple control web page,
and an optional Ethernet cable to a "partner device" box. Pastel accent colours, clear arrows showing data direction.
```
- 비율: `--ar 16:9`
- 연결은 `docs/spec.md` 4장과 6.1(P3안: 브라우저 렌더러 + Python 브리지)을 따른다. 외부 기기 연동은 아직 제안 단계다.

### P9. 2주 차 벤치 시제품 (현실적인 중간 모습)

```text
Realistic photo of an early optical bench test on a lab table: a smartphone lying face-up showing a white checkerboard,
a sheet of half-mirror acrylic held at 45 degrees by a cardboard stand, a grey retroreflective sheet taped upright behind it,
a black cloth hood partly covering the setup, a handheld lux meter and a ruler nearby.
A faint floating copy of the checkerboard appears in the air in front of the acrylic. Office lighting, slightly messy, honest prototype look.
```
- 비율: `--ar 3:2`
- `research/07-test-plan.md` 4장(B-01)의 배치와 같다. 실제로 이렇게 보일지는 B-01 시험으로 확인한다.

---

## 4. 도구별 붙여 쓰기

| 도구 | 조립 방법 | 권장 설정 |
|---|---|---|
| Midjourney | `[공통 블록] [장면] --ar … --style raw --no beam, cone of light, neon, text, logo` | `--style raw`로 과장을 줄인다. 형태를 맞추려면 같은 시드를 다시 쓴다 (`--seed`) |
| GPT 이미지 / DALL·E 계열 | 공통 블록 + 장면 + `Avoid: …` 문장 | "photorealistic product photo"를 맨 앞에 둔다. 한 번에 한 장면씩 |
| Gemini / Imagen 계열 | 위와 같다 | 비율은 UI에서 고른다 |
| Stable Diffusion / Flux | positive = 공통 + 장면, negative = §2 | CFG는 중간값. 형태가 무너지면 P4 단면도를 ControlNet(lineart) 입력으로 쓴다 |

### 일관성을 유지하는 순서
1. **P1을 먼저** 여러 장 뽑는다.
2. 사양에 가장 가까운 한 장을 고른다 (§5 체크리스트로).
3. 그 이미지를 **참조 이미지**로 지정한다 (Midjourney `--cref`/`--sref` 또는 각 도구의 이미지 참조 기능). 이렇게 해야 P2·P3·P5가 같은 제품으로 보인다.

---

## 5. 생성 결과 판정 체크리스트

다음 중 **필수 항목**을 하나라도 어기면 버리고 다시 뽑는다.

| # | 항목 | 필수 |
|---|---|---|
| 1 | 빛줄기·원뿔·레이저가 없다 | ✔ |
| 2 | 상이 유리창 **앞** 허공에 있다 (유리 안이나 위가 아님) | ✔ |
| 3 | 상에 테두리나 화면 베젤이 없다 | ✔ |
| 4 | 상 아래 받침대에 위를 향한 소자 격자가 있다 | ✔ |
| 5 | 밝은 실내 조명이다 (어두운 무대가 아님) | ✔ |
| 6 | 손가락이 상과 같은 깊이에 있다 (P2·P3) | ✔ |
| 7 | 손가락이 5개이고 모양이 정상이다 | ✔ |
| 8 | 얼굴, 실존 브랜드 로고, 의미 없는 글자가 없다 | ✔ |
| 9 | 상이 화면보다 약간 어둡고 평평하게 읽힌다 | 권장 |
| 10 | 전체 크기가 책상 위 노트북과 비교해 비슷하다 (약 40 cm 이내) | 권장 |

---

## 6. 이 프롬프트가 보장하지 **않는** 것

1. **실제 밝기와 대비.** 이미지 모델은 상을 실제보다 밝고 선명하게 그리는 경향이 있다 (추정). 실제 값은 B-01 벤치 시험으로 잰다.
2. **치수 정확도.** 프롬프트의 cm 값은 대략적인 지시일 뿐이다.
3. **광학적 정확성.** P4의 광선 경로는 개념도다. 정식 단면도는 사양 파일에서 계산한다.
4. **최종 외형.** 외함 재질과 형태는 아직 정해지지 않았다 (`docs/spec.md` 7장 "기구·외함").
