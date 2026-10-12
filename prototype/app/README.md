# prototype/app

호스트 소프트웨어: GLB 로딩·렌더링, 손 좌표 수신, 가상 버튼 판정, 햅틱 이벤트 송신, 조도 기반 밝기 조절, CSV 로그 (프롬프트 E1·E2).

- 플랫폼/호스트: [미정 — Unity/Unreal/WebGPU/Python/C++ · PC/Jetson/Raspberry Pi 등]
- 가상 버튼 상태기계: idle → hover → arm → activate, 그리고 cancel / tracking-lost / safety-stop (프롬프트 E2).
- 로그는 `prototype/test-data/log-template.csv` 열 규약을 따른다.
- 설치·실행 절차: [작성 예정]
