# prototype/test-data

원시 시험 로그를 둔다. 가공·요약하지 않은 원본을 그대로 보존한다.

- 열 규약: `log-template.csv` (README 5장 실험 로그 열)
- 파일 이름: `YYYYMMDD-<시험ID>-<build_id>.csv` (예: `20261020-T-07-a1b2c3d.csv`)
- `timestamp`는 ISO 8601 + 시간대 (예: `2026-10-20T14:03:12.345+09:00`)
- 단위: `frame_ms`/`touch_latency_ms` = ms, `power_w` = W, `temperature_c` = °C, `ambient_lux` = lux
- `display_brightness`의 단위(cd/m² 실측 또는 설정값 %)는 시험마다 `operator_note`에 명시한다.
