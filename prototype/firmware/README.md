# prototype/firmware

햅틱 어레이 구동, 조도 센서, 전력 관리, 안전 인터록 등 마이크로컨트롤러 측 코드를 둔다.

- 아키텍처 결정(`research/04-architecture.md`) 전에는 코드를 추가하지 않는다.
- 각 모듈은 `04-architecture.md` 3장의 인터페이스 명세(업데이트율, 지연 예산, fail-safe 동작)를 따른다.
- 초음파·고전압 출력 경로는 `docs/safety-checklist.md` 통과 전 최종 시스템에 연결하지 않는다.
- 빌드·플래시 절차: [작성 예정]
