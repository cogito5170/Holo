# 디자인 시안 프롬프트 — 물리적으로 가능한 비(非)박스 형태

- 목적: 공중에 뜬 평면 상 + 비접촉 터치 + 초음파 햅틱을, 상자가 아닌 형태로 디자인 시안을 뽑기 위한 이미지 생성 프롬프트
- 작성일: 2026-10-12
- 관계: `docs/visual-prompts.md`는 박스형(재귀반사, A2) 기준이다. 형태를 바꾸면서 이 문서로 대체한다.

> **표기 규칙.** 이 프롬프트로 만든 이미지는 **디자인 컨셉 렌더**다. 실물 사진이나 검증된 설계가 아니다.
> 보고서·발표에 쓸 때는 캡션에 `디자인 시안 — 생성 모델 출력, 실물 아님`을 붙인다.

---

## 0. 박스가 아닌 형태가 가능한 이유와 조건

앞의 박스형은 **재귀반사 방식(AIRR)** 때문에 생긴 형태다. 이 방식은 다음 세 가지가 서로 다른 면에 놓여야 해서 깊은 상자가 된다.
- 패널
- 45° 하프미러
- 뒷벽 재귀반사 시트

**공중결상 플레이트**(이면 코너 반사 어레이, dihedral corner reflector array)를 쓰면 판 한 장이 결상을 맡는다. 그래서 다음 형태가 가능해진다.
- 얇은 쐐기
- 책상 매립
- 둥근 외형
- 고리
- 액자

**전제 조건:**
- 플레이트의 가격·크기·공급처는 아직 확인하지 못했다 (`docs/spec.md` 7장: 결상 광학 15만 원 배분).
- 이 시안들은 **플레이트를 확보할 수 있다는 가정** 위에 있다.
- 플레이트를 구하지 못하면 재귀반사 방식으로 돌아가야 하고, 그러면 같은 형태라도 더 두꺼워진다.

---

## 1. 모든 시안이 지켜야 하는 물리 규칙

이미지 모델은 이 규칙을 모른다. 그래서 공통 블록(§2)에 문장으로 박아 넣었다.

| # | 규칙 | 디자인에 주는 뜻 |
|---|---|---|
| R1 | 공중 상은 **평평한 카드 한 장**이다. 화면을 공중으로 옮긴 것이다 | 입체감은 3D 렌더링(음영·회전)으로 낸다. 구름처럼 퍼진 홀로그램은 안 된다 |
| R2 | 상은 플레이트를 기준으로 **화면과 대칭인 위치**에 뜬다. 화면이 판 아래 10 cm 에 있으면 상은 판 위 10 cm 에 뜬다 | 판 바로 아래에, 상이 뜨는 거리만큼의 **숨은 공간**(쐐기 모양)이 필요하다 |
| R3 | 플레이트는 화면 빛이 **비스듬히** 들어와야 결상한다. 화면을 판과 평행하게 두면 잘 안 된다 (기억 수준, 확인 필요) | 화면은 판 아래에서 대략 30–60° 기울인다. 그래서 상도 판 위에서 같은 각도로 기운다 |
| R4 | 상은 **플레이트를 통해 볼 때만** 보인다. 시선 뒤로 플레이트가 배경처럼 있어야 한다. 옆이나 뒤에서는 보이지 않는다 | 사용자 시선 방향이 디자인을 정한다. 측면 렌더에서는 상이 사라지거나 일부만 보여야 사실적이다 |
| R5 | 상은 화면보다 **어둡다**. 밝은 실내(500 lux)에서는 플레이트 주변을 어둡게 하거나 가림이 있어야 잘 보인다 | 판 주변은 무광 흑색, 테두리·차양은 디자인 요소로 쓴다 |
| R6 | 초음파 햅틱 소자는 손끝까지 **막힘 없는 직선 경로**가 있어야 하고, 10–20 cm 안에 있어야 한다. 판을 통과해서는 못 쏜다 | 소자 격자는 상 **바로 아래 앞쪽 테두리**나 **위쪽 고리** 안쪽에 둔다 |
| R7 | 손 추적 센서는 손을 직접 봐야 한다 | 앞 테두리나 고리 안쪽에 작은 센서 창이 있다 |
| R8 | 빛줄기·레이저·원뿔 빔은 **보이지 않는다**. 초음파도 보이지 않는다 | 이미지에 빔이 있으면 틀린 시안이다 |
| R9 | 비상정지 버튼은 손이 닿는 곳에 있다 (README 안전 원칙) | 작게라도 형태 안에 넣는다 |

---

## 2. 공통 블록 (모든 시안 프롬프트 앞에 붙인다)

```text
Industrial design concept render of a desktop mid-air display that uses a flat "aerial imaging plate":
a thin dark glass-like plate with a fine micro-mirror grid texture, flush with the product surface.
A flat, crisp, glowing image card (about 15 cm wide) floats in the air above or in front of the plate, tilted about 45 degrees toward the viewer,
showing a softly shaded rotating 3D object and a few small circular buttons. The image is slightly dimmer than a phone screen,
has no frame and no glow cone, and the plate is visible behind it as a dark backdrop.
A slim row of small round ultrasonic transducers sits in the product's front edge right below the floating image, facing the user's fingertip,
and a small dark sensor window for hand tracking sits next to it. A small red emergency-stop button is integrated discreetly.
No light beams, no lasers, no visible ultrasound. Realistic materials, soft studio lighting in a bright modern office (about 500 lux).
```

**한국어 요약:**
- 책상 위 제품의 표면에 미세 격자 무늬가 있는 어두운 결상판이 묻혀 있다.
- 판 앞·위 허공에 대각 약 15 cm의 평평한 상 카드가 사용자 쪽으로 45° 기울어 떠 있다. 상에는 음영 처리된 3D 물체와 작은 원형 버튼이 있다.
- 상 바로 아래 앞 테두리에 초음파 소자 줄과 손 추적 센서 창, 작은 비상정지 버튼이 있다.
- 빔은 없다. 밝은 사무실 조명이다.

---

## 3. 금지 목록

```text
box-shaped cabinet, arcade machine, sci-fi hologram, blue light beam, cone of light, projector rays, laser beams,
volumetric fog, glowing particles, transparent ghost person, Iron Man style UI, neon cyberpunk, dark stage,
image floating with no plate behind it, image visible from the back side, spinning parts, VR headset,
smartphone hologram pyramid, text, watermark, logo, brand names, extra fingers, distorted hands
```

- 네거티브 칸이 있는 도구 (Stable Diffusion·Flux): 위 목록을 그대로 넣는다.
- 네거티브 칸이 없는 도구: 프롬프트 끝에 `Avoid: box-shaped cabinet, sci-fi hologram beams, light cones, neon, text, logos.`를 붙인다.
- Midjourney: `--no box cabinet, beam, cone of light, neon, text, logo`를 쓴다.

---

## 4. 시안별 프롬프트

각 시안은 **[공통 블록] + 시안 문장 + [금지 목록]**으로 조립한다.

### D1. 슬림 웨지 (Slim Wedge) — 책상 위 독서대 형태

```text
Form: a low, slim wedge like a premium book stand, about 32 cm wide, 22 cm deep, rising from 2 cm at the front to 12 cm at the back.
The sloped top surface is the aerial imaging plate framed by a thin anodised aluminium bezel in graphite grey.
The display is hidden inside the wedge under the plate. The floating image hovers about 8 cm above the plate, leaning toward the seated user.
The front lip is a soft rounded edge holding the ultrasonic transducer strip and the hand-tracking window.
Three-quarter front view from a seated eye height, minimal oak desk, laptop blurred in the background.
```
- 비율: `--ar 3:2`
- 한 줄 요약: 얇은 쐐기. 기울어진 윗면이 결상판이고 상은 그 위에 뜬다.
- 물리 메모: 쐐기 높이는 상이 뜨는 거리(R2)와 화면 크기에서 정해진다. 12 cm 높이는 상 거리 약 8 cm 를 가정한 **추정**이다.

### D2. 책상 매립형 (Flush Desk Inlay)

```text
Form: the product disappears into the desk. A rectangular aerial imaging plate, about 20 x 14 cm, is set flush into a light oak desktop
with a hairline black border. The floating image rises about 10 cm above the desk surface at a 45 degree tilt toward the user.
Just in front of the plate, a narrow flush strip in the desk holds the ultrasonic transducers and the sensor window; a tiny red stop button sits at the strip's end.
Nothing else is visible above the desk. High three-quarter view, clean workspace, natural daylight.
```
- 비율: `--ar 16:9`
- 한 줄 요약: 책상 면에 판이 묻혀 있고 상이 책상 위로 떠오른다. 장치 본체는 상판 아래에 있다.
- 물리 메모: 상판 아래에 쐐기 모양 공간(깊이 약 10–15 cm, 추정)과 환기가 필요하다. 책상 가공이 필요하므로 이동형 데스크톱 요구와 충돌한다.

### D3. 오브 (Orb / Pebble) — 둥근 외형

```text
Form: a smooth pebble-shaped object, like a large polished river stone, about 30 cm wide and 14 cm tall, in matte warm-grey ceramic finish.
A flat elliptical aerial imaging plate is inset into its gently sloped front-top face, framed by a thin dark ring.
The floating image hovers above the plate, leaning toward the viewer. A slim arc of ultrasonic transducers follows the front curve under the image,
with the hand-tracking window centred in the arc. Soft studio light, shallow depth of field, side table in a bright living room.
```
- 비율: `--ar 4:3`
- 한 줄 요약: 조약돌 같은 둥근 외형이다. 결상판만 평평하고 상은 그 위에 뜬다.
- 물리 메모: 외형은 둥글어도 **결상판은 평평해야 한다**. 곡면 판으로는 결상하지 않는다 (R1·R2). 판 둘레의 둥근 테두리가 주변광을 일부 가린다 (R5).

### D4. 아치 (Halo Arch) — 상이 고리 안에 뜬다

```text
Form: a low flat base (32 x 22 cm, 4 cm tall) with an aerial imaging plate on top, and a slender semicircular arch rising over it,
about 26 cm tall, in brushed light aluminium with a matte black inner face.
The floating image hovers inside the arch opening, framed by it like a halo. The ultrasonic transducers line the inner top of the arch, pointing down at the user's hand,
and a tiny sensor window sits at the arch apex. The inner black face of the arch shades the image from ceiling light.
Front three-quarter view, gallery-like bright white room.
```
- 비율: `--ar 4:5`
- 한 줄 요약: 납작한 받침의 판 위에 아치가 서 있고, 상이 아치 안에 뜬다. 햅틱은 아치 안쪽 위에서 손등 쪽으로 쏜다.
- 물리 메모: 위에서 아래로 쏘면 **손등**에 촉감이 온다. 손바닥이나 손끝 패드에 주려면 앞 테두리 배치(D1)가 낫다. 아치 안쪽 흑색 면은 차양 역할을 한다 (R5).

### D5. 스탠딩 프레임 (Standing Frame) — 액자처럼 세움

```text
Form: a slim standing frame like a modern picture frame, 30 cm wide and 24 cm tall, with a thin aerial imaging plate as its face,
leaning back slightly on a tapered rear body (like the back of a desktop monitor, 9 cm deep at the base, thinner at the top).
The floating image hovers about 8 cm in front of the frame, tilted, at seated eye level. A narrow foot in front of the frame holds the ultrasonic transducer strip
pointing up toward the image and the hand-tracking window. Side-front view on a desk, soft daylight.
```
- 비율: `--ar 3:2`
- 한 줄 요약: 액자처럼 세운 판. 뒤쪽 몸체에 화면이 기울어져 숨어 있고, 상은 판 앞에 뜬다.
- 물리 메모: 화면이 판과 평행하면 결상이 잘 안 되므로 뒤쪽 몸체 안에서 기울어 있어야 한다 (R3). 그래서 뒷면은 아래가 두꺼운 테이퍼 모양이 된다.

---

## 5. 같은 시안으로 장면 더 뽑기

D1–D5 중 고른 시안의 형태 문장을 넣고, 장면 문장만 바꿔 붙인다.

### 사용 장면 (손가락으로 누름)
```text
Scene: a person seated at the desk (face out of frame) gently touches one floating button with the tip of the index finger.
The fingertip is exactly at the depth of the floating image; the touched button shows a thin bright ring. Natural office daylight.
```

### 측면 시점 (사실성 확인용)
```text
Scene: strict side view at 80 degrees from the front. From this angle the floating image is NOT visible (only a faint edge or nothing),
showing honestly that the image can only be seen from the front through the plate.
```

### 분해도
```text
Scene: exploded axonometric view on light grey: outer shell, aerial imaging plate, hidden display tilted at 45 degrees under the plate,
matte black light trap, ultrasonic transducer strip with driver board, hand-tracking sensor, microcontroller, emergency-stop button, power input.
Thin leader lines, no text labels.
```

---

## 6. 일관성 유지와 도구별 사용

**순서:**
1. 시안 D1–D5 각각 대표컷을 3–4장씩 뽑는다.
2. §7 체크리스트로 거른다.
3. 고른 한 장을 참조 이미지로 지정한다 (`--cref`/`--sref` 또는 도구의 이미지 참조 기능).
4. 그 상태에서 §5 장면을 뽑는다.

**도구별 메모:**

| 도구 | 방법 |
|---|---|
| Midjourney | `--style raw`, 비율은 시안별 값, 같은 `--seed`로 변형 비교 |
| GPT 이미지 / Gemini 계열 | 맨 앞에 `photorealistic industrial design render`를 둔다. 한 번에 한 시안만 |
| SD / Flux | negative = §3. 형태가 무너지면 실루엣 스케치를 ControlNet 입력으로 쓴다 |

---

## 7. 생성 결과 판정 체크리스트

| # | 항목 | 필수 |
|---|---|---|
| 1 | 상자·아케이드 기계처럼 보이지 않는다 | ✔ |
| 2 | 상 뒤(시선 방향)에 **평평한 결상판**이 배경으로 있다 (R4) | ✔ |
| 3 | 상은 평평한 카드다. 구름이나 원뿔 같은 홀로그램이 아니다 (R1) | ✔ |
| 4 | 빛줄기·레이저·보이는 초음파가 없다 (R8) | ✔ |
| 5 | 판 아래·뒤에 화면이 숨을 만한 두께가 형태에 있다 (R2·R3) | ✔ |
| 6 | 소자 줄이 상 근처에 있고, 판에 가려지지 않은 방향으로 손을 향한다 (R6) | ✔ |
| 7 | 손가락이 상과 같은 깊이에 있고 모양이 정상이다 (사용 장면) | ✔ |
| 8 | 얼굴·실존 로고·의미 없는 글자가 없다 | ✔ |
| 9 | 측면 시점에서 상이 거의 안 보인다 (§5 측면 장면) | 권장 |
| 10 | 상 주변이 어둡거나 가려져 밝은 방에서도 읽힌다 (R5) | 권장 |

---

## 8. 이 프롬프트가 보장하지 않는 것

1. **공중결상 플레이트의 가격·크기 확보.** 시안 전부가 이것에 의존한다. 1주 차 견적에서 먼저 확인할 항목이다.
2. **치수.** 프롬프트의 cm 값은 형태 지시일 뿐이다. 실제 치수는 플레이트 크기·화면 크기·상 거리에서 계산해 정한다.
3. **R3(비스듬한 입사)의 정량 조건.** 기억에 근거한 규칙이라 원문과 데이터시트로 확인해야 한다.
4. **밝기와 대비.** 생성 이미지는 실제보다 밝고 선명하게 그리는 경향이 있다 (추정).
