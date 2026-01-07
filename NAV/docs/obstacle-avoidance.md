# 🚧 장애물 회피 알고리즘 상세 순서도

## 1. IR 센서 사양

### 송신부 (TX LED)

| Parameter | Value | Note |
|-----------|-------|------|
| 파장 | 940nm | 근적외선 |
| 구동 주파수 | 38kHz | PWM 변조 |
| 구동 전류 | 20~100mA | 거리에 따라 조절 |
| 빔 각도 | 20°~30° | SMD 타입 |
| 채널 수 | 20개 | 범퍼 전면 배치 |
| 스캔 방식 | 순차 멀티플렉싱 | ~50ms/전체 스캔 |

### 수신부 (IR Receiver)

| Parameter | Value | Note |
|-----------|-------|------|
| 호환 IC | TSOP38238 / VS1838B | - |
| 수신 파장 | 940nm ±50nm | IR LED와 매칭 |
| 중심 주파수 | 38kHz | 대역통과 필터 |
| AGC | 내장 | 자동 게인 제어 |
| 출력 | Active Low | 감지 시 LOW |
| 응답 시간 | ~300µs | - |

### 감지 범위

| Distance | Signal Strength | Reliability |
|----------|----------------|-------------|
| 0-2cm | Very Strong | 포화 가능 |
| 2-10cm | Strong | ★★★★★ |
| 10-25cm | Medium | ★★★★☆ |
| 25-40cm | Weak | ★★★☆☆ |
| >40cm | Very Weak | 불안정 |

---

## 2. 메인 장애물 감지 루프

```mermaid
flowchart TD
    START((🔄 스캔 루프)) --> ENABLE["TX Enable<br/>(채널 N 활성화)"]
    
    ENABLE --> WAIT["대기 210µs<br/>(8 펄스)"]
    WAIT --> READ1{RX 출력?}
    
    READ1 -->|HIGH| NO_OBS["장애물 없음"]
    READ1 -->|LOW| VERIFY["검증 대기 395µs<br/>(15 펄스 추가)"]
    
    VERIFY --> READ2{RX 출력?}
    READ2 -->|HIGH| NOISE["노이즈로 판단"]
    READ2 -->|LOW| CONFIRMED["✅ 장애물 확인"]
    
    NO_OBS --> NEXT_CH
    NOISE --> NEXT_CH
    CONFIRMED --> RECORD["감지 채널 기록"]
    RECORD --> NEXT_CH
    
    NEXT_CH["채널 N+1"] --> CHECK_ALL{모든 채널<br/>완료?}
    CHECK_ALL -->|No| ENABLE
    CHECK_ALL -->|Yes| ANALYZE["감지 패턴 분석"]
    
    ANALYZE --> ACTION["회피 동작 결정"]
    ACTION --> EXECUTE["모터 제어"]
    EXECUTE --> DELAY["스캔 주기 대기<br/>(~50ms)"]
    DELAY --> START
    
    style CONFIRMED fill:#ff6b6b,color:#fff
    style NOISE fill:#ffd43b,color:#000
```

## 3. 채널별 장애물 위치 판단

```mermaid
flowchart TD
    INPUT["감지된 채널 목록"] --> CLASSIFY{채널 분류}
    
    CLASSIFY --> CH1_8{Ch 1-8<br/>감지?}
    CLASSIFY --> CH9_12{Ch 9-12<br/>감지?}
    CLASSIFY --> CH13_20{Ch 13-20<br/>감지?}
    
    CH1_8 -->|Yes| LEFT["🔶 좌측 장애물"]
    CH9_12 -->|Yes| FRONT["🔴 정면 장애물"]
    CH13_20 -->|Yes| RIGHT["🔶 우측 장애물"]
    
    LEFT --> COMBINE
    FRONT --> COMBINE
    RIGHT --> COMBINE
    
    COMBINE["조합 분석"] --> PATTERN{패턴?}
    
    PATTERN -->|"Ch1-8 only"| LEFT_ONLY["좌측만"]
    PATTERN -->|"Ch13-20 only"| RIGHT_ONLY["우측만"]
    PATTERN -->|"Ch9-12 only"| FRONT_ONLY["정면만"]
    PATTERN -->|"Ch1-12"| LEFT_FRONT["좌측+정면<br/>(ㄱ 코너)"]
    PATTERN -->|"Ch9-20"| RIGHT_FRONT["정면+우측<br/>(ㄴ 코너)"]
    PATTERN -->|"Ch1-8 + Ch13-20"| BOTH_SIDES["양측<br/>(통로)"]
    PATTERN -->|"All channels"| SURROUNDED["전방위<br/>(막다른 곳)"]
```

## 4. 시나리오별 회피 알고리즘

### Scenario 1: 정면 벽

```mermaid
flowchart TD
    DETECT["🚨 정면 감지<br/>(Ch 9-12)"] --> STOP["🛑 즉시 정지"]
    
    STOP --> DISTANCE{거리?}
    DISTANCE -->|"> 10cm"| SLOW_APPROACH["저속 접근<br/>(벽 청소)"]
    DISTANCE -->|"< 10cm"| BACKUP["후진 5cm"]
    
    SLOW_APPROACH --> TOUCH{범퍼<br/>접촉?}
    TOUCH -->|No| SLOW_APPROACH
    TOUCH -->|Yes| BACKUP
    
    BACKUP --> SCAN_SIDES["좌/우 스캔"]
    
    SCAN_SIDES --> SPACE{여유 공간?}
    SPACE -->|"좌측 여유"| TURN_LEFT["↺ 90° 좌회전"]
    SPACE -->|"우측 여유"| TURN_RIGHT["↻ 90° 우회전"]
    SPACE -->|"양쪽 여유"| RANDOM["랜덤 방향"]
    SPACE -->|"양쪽 막힘"| TURN_180["↻ 180° 회전"]
    
    TURN_LEFT --> WALL_FOLLOW["벽 따라가기 모드"]
    TURN_RIGHT --> WALL_FOLLOW
    RANDOM --> RESUME["정상 주행"]
    TURN_180 --> RESUME
    
    WALL_FOLLOW --> RESUME
    
    style DETECT fill:#ff6b6b,color:#fff
```

### Scenario 2: 좌측 장애물

```mermaid
flowchart TD
    DETECT["🚨 좌측 감지<br/>(Ch 3-6)"] --> INTENSITY{신호 강도?}
    
    INTENSITY -->|"강함<br/>(< 15cm)"| STRONG_LEFT["가까운 장애물"]
    INTENSITY -->|"약함<br/>(> 15cm)"| WEAK_LEFT["먼 장애물"]
    
    STRONG_LEFT --> SLOW["감속 50%"]
    SLOW --> STEER_R["우측 조향 +20°"]
    STEER_R --> CHECK1{클리어?}
    CHECK1 -->|No| STEER_R
    CHECK1 -->|Yes| RESUME
    
    WEAK_LEFT --> SLIGHT_R["미세 우측 +5°"]
    SLIGHT_R --> MONITOR["계속 모니터링"]
    MONITOR --> CHECK2{강도 증가?}
    CHECK2 -->|Yes| STRONG_LEFT
    CHECK2 -->|No| RESUME["정상 주행"]
    
    style DETECT fill:#ffd43b,color:#000
```

### Scenario 3: 우측 장애물

```mermaid
flowchart TD
    DETECT["🚨 우측 감지<br/>(Ch 14-17)"] --> INTENSITY{신호 강도?}
    
    INTENSITY -->|"강함<br/>(< 15cm)"| STRONG_RIGHT["가까운 장애물"]
    INTENSITY -->|"약함<br/>(> 15cm)"| WEAK_RIGHT["먼 장애물"]
    
    STRONG_RIGHT --> SLOW["감속 50%"]
    SLOW --> STEER_L["좌측 조향 -20°"]
    STEER_L --> CHECK1{클리어?}
    CHECK1 -->|No| STEER_L
    CHECK1 -->|Yes| RESUME
    
    WEAK_RIGHT --> SLIGHT_L["미세 좌측 -5°"]
    SLIGHT_L --> MONITOR["계속 모니터링"]
    MONITOR --> CHECK2{강도 증가?}
    CHECK2 -->|Yes| STRONG_RIGHT
    CHECK2 -->|No| RESUME["정상 주행"]
    
    style DETECT fill:#ffd43b,color:#000
```

### Scenario 4: 코너 진입 (ㄱ자)

```mermaid
flowchart TD
    DETECT["🚨 좌측+정면 감지<br/>(Ch 1-12)"] --> IDENTIFY["ㄱ자 코너 인식"]
    
    IDENTIFY --> STOP["정지"]
    STOP --> BACKUP["후진 3cm"]
    
    BACKUP --> TURN_R["↻ 우회전 시작"]
    TURN_R --> SCAN{정면<br/>클리어?}
    SCAN -->|No| TURN_R
    SCAN -->|Yes| ANGLE_CHECK{회전 각도?}
    
    ANGLE_CHECK -->|"~90°"| WALL_MODE["벽 따라가기"]
    ANGLE_CHECK -->|"> 90°"| ADJUST["각도 조정"]
    
    ADJUST --> WALL_MODE
    WALL_MODE --> EDGE_CLEAN["코너 엣지 청소"]
    EDGE_CLEAN --> RESUME["정상 주행"]
    
    style DETECT fill:#ff922b,color:#fff
```

### Scenario 5: 코너 진입 (ㄴ자)

```mermaid
flowchart TD
    DETECT["🚨 정면+우측 감지<br/>(Ch 9-20)"] --> IDENTIFY["ㄴ자 코너 인식"]
    
    IDENTIFY --> STOP["정지"]
    STOP --> BACKUP["후진 3cm"]
    
    BACKUP --> TURN_L["↺ 좌회전 시작"]
    TURN_L --> SCAN{정면<br/>클리어?}
    SCAN -->|No| TURN_L
    SCAN -->|Yes| ANGLE_CHECK{회전 각도?}
    
    ANGLE_CHECK -->|"~90°"| WALL_MODE["벽 따라가기"]
    ANGLE_CHECK -->|"> 90°"| ADJUST["각도 조정"]
    
    ADJUST --> WALL_MODE
    WALL_MODE --> EDGE_CLEAN["코너 엣지 청소"]
    EDGE_CLEAN --> RESUME["정상 주행"]
    
    style DETECT fill:#ff922b,color:#fff
```

### Scenario 6: 좁은 통로 (양측 장애물)

```mermaid
flowchart TD
    DETECT["🚨 양측 감지<br/>(Ch 1-8 + Ch 13-20)"] --> ANALYZE["통로 폭 분석"]
    
    ANALYZE --> WIDTH{통로 폭?}
    
    WIDTH -->|"> 로봇 폭 +5cm"| PASSABLE["통과 가능"]
    WIDTH -->|"< 로봇 폭 +5cm"| TOO_NARROW["통과 불가"]
    
    PASSABLE --> CENTER_ALIGN["중앙 정렬"]
    CENTER_ALIGN --> BALANCE{좌/우<br/>균형?}
    BALANCE -->|"좌측 더 가까움"| SLIGHT_R["미세 우측"]
    BALANCE -->|"우측 더 가까움"| SLIGHT_L["미세 좌측"]
    BALANCE -->|"균등"| STRAIGHT["직진"]
    
    SLIGHT_R --> SLOW_FWD["저속 직진"]
    SLIGHT_L --> SLOW_FWD
    STRAIGHT --> SLOW_FWD
    
    SLOW_FWD --> EXIT{통로<br/>탈출?}
    EXIT -->|No| CENTER_ALIGN
    EXIT -->|Yes| RESUME["정상 주행"]
    
    TOO_NARROW --> TURN_BACK["180° 회전"]
    TURN_BACK --> FIND_ALT["대체 경로 탐색"]
    
    style DETECT fill:#74c0fc,color:#fff
```

### Scenario 7: 막다른 곳 (전방위 장애물)

```mermaid
flowchart TD
    DETECT["🚨 전방위 감지<br/>(All Channels)"] --> EMERGENCY["⚠️ 긴급 상황"]
    
    EMERGENCY --> STOP["완전 정지"]
    STOP --> SCAN_360["360° 스캔"]
    
    SCAN_360 --> FIND_GAP{틈 발견?}
    
    FIND_GAP -->|Yes| CALC_ANGLE["탈출 각도 계산"]
    FIND_GAP -->|No| DESPERATION["최소 신호 방향"]
    
    CALC_ANGLE --> ROTATE["해당 방향 회전"]
    DESPERATION --> ROTATE
    
    ROTATE --> ATTEMPT_EXIT["저속 탈출 시도"]
    ATTEMPT_EXIT --> SUCCESS{탈출?}
    
    SUCCESS -->|Yes| RESUME["정상 주행"]
    SUCCESS -->|No| RETRY_COUNT{재시도<br/>횟수?}
    
    RETRY_COUNT -->|"< 3"| SCAN_360
    RETRY_COUNT -->|"≥ 3"| HELP["🆘 도움 요청<br/>(알림 전송)"]
    
    style DETECT fill:#ff0000,color:#fff
    style EMERGENCY fill:#ff6b6b,color:#fff
    style HELP fill:#ff0000,color:#fff
```

### Scenario 8: 낭떠러지 감지 (클리프 센서)

```mermaid
flowchart TD
    SCAN["바닥 IR 스캔"] --> REFLECT{반사 신호?}
    
    REFLECT -->|"정상 반사"| SAFE["✅ 안전"]
    REFLECT -->|"약한/없음"| CLIFF["⚠️ 낭떠러지!"]
    
    SAFE --> CONTINUE["계속 이동"]
    
    CLIFF --> WHICH{감지 위치?}
    
    WHICH -->|"전면 좌측"| CLIFF_FL["좌측 낭떠러지"]
    WHICH -->|"전면 우측"| CLIFF_FR["우측 낭떠러지"]
    WHICH -->|"전면 전체"| CLIFF_FRONT["정면 낭떠러지"]
    
    CLIFF_FL --> E_STOP["🛑 긴급 정지"]
    CLIFF_FR --> E_STOP
    CLIFF_FRONT --> E_STOP
    
    E_STOP --> BACKUP["후진 10cm"]
    
    BACKUP --> ESCAPE{탈출 방향?}
    ESCAPE -->|좌측 낭떠러지| TURN_R90["↻ 90° 우회전"]
    ESCAPE -->|우측 낭떠러지| TURN_L90["↺ 90° 좌회전"]
    ESCAPE -->|정면 낭떠러지| TURN_180["↻ 180° 회전"]
    
    TURN_R90 --> SAFE_ZONE["안전 구역 이동"]
    TURN_L90 --> SAFE_ZONE
    TURN_180 --> SAFE_ZONE
    
    SAFE_ZONE --> CONTINUE
    
    style CLIFF fill:#ff0000,color:#fff
    style E_STOP fill:#ff0000,color:#fff
```

### Scenario 9: 동적 장애물 (사람/반려동물)

```mermaid
flowchart TD
    SCAN["IR 스캔"] --> DETECT{장애물?}
    DETECT -->|No| SCAN
    DETECT -->|Yes| MEASURE["거리 측정 T1"]
    
    MEASURE --> WAIT["100ms 대기"]
    WAIT --> MEASURE2["거리 측정 T2"]
    
    MEASURE2 --> DELTA{거리 변화?}
    
    DELTA -->|"D2 < D1<br/>(접근 중)"| DYNAMIC["🏃 동적 장애물"]
    DELTA -->|"D2 > D1<br/>(이탈 중)"| DEPARTING["장애물 이탈 중"]
    DELTA -->|"D2 ≈ D1"| STATIC["🪨 정적 장애물"]
    
    DYNAMIC --> FULL_STOP["완전 정지"]
    FULL_STOP --> WAIT_3S["3초 대기"]
    WAIT_3S --> RECHECK{여전히<br/>감지?}
    RECHECK -->|Yes| POLITE_WAIT["추가 대기<br/>(최대 10초)"]
    RECHECK -->|No| RESUME["주행 재개"]
    
    POLITE_WAIT --> TIMEOUT{타임아웃?}
    TIMEOUT -->|No| RECHECK
    TIMEOUT -->|Yes| GENTLE_AVOID["천천히 우회"]
    GENTLE_AVOID --> RESUME
    
    DEPARTING --> SLOW_RESUME["저속 재개"]
    SLOW_RESUME --> RESUME
    
    STATIC --> NORMAL_AVOID["일반 회피"]
    NORMAL_AVOID --> RESUME
    
    style DYNAMIC fill:#ffd43b,color:#000
    style FULL_STOP fill:#ff6b6b,color:#fff
```

---

## 5. 센서 채널 맵핑 다이어그램

```
                      전면 (Front)
              ┌─────────────────────────┐
              │                         │
          ┌───┤  [9] [10] [11] [12]    ├───┐
          │   │                         │   │
          │ ┌─┤ [8]               [13] ├─┐ │
          │ │ │                         │ │ │
        좌│ │ │ [7]               [14] │ │ │우
        측│ │ │                         │ │ │측
          │ │ │ [6]               [15] │ │ │
          │ │ │                         │ │ │
          │ │ │ [5]               [16] │ │ │
          │ └─┤                         ├─┘ │
          │   │ [4]               [17] │   │
          └───┤                         ├───┘
              │ [3]               [18] │
              │                         │
              │ [2]               [19] │
              │                         │
              │ [1]               [20] │
              └─────────────────────────┘
                      후면 (Rear)


    채널 그룹:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Ch 1-4   : 좌측 후방  (Left Rear)
    Ch 5-8   : 좌측 전방  (Left Front)
    Ch 9-12  : 정면       (Center Front)
    Ch 13-16 : 우측 전방  (Right Front)
    Ch 17-20 : 우측 후방  (Right Rear)
```

## 6. 회피 우선순위

```mermaid
flowchart TD
    subgraph PRIORITY["⚡ 회피 우선순위"]
        P1["1️⃣ 낭떠러지<br/>(최우선)"]
        P2["2️⃣ 정면 충돌 임박"]
        P3["3️⃣ 동적 장애물"]
        P4["4️⃣ 정적 장애물"]
        P5["5️⃣ Force Field<br/>(스테이션)"]
    end
    
    P1 --> |"즉시 정지 + 후진"| A1["긴급 회피"]
    P2 --> |"정지 + 방향 전환"| A2["충돌 회피"]
    P3 --> |"정지 + 대기"| A3["예의 바른 대기"]
    P4 --> |"조향 + 우회"| A4["일반 회피"]
    P5 --> |"회전 + 이탈"| A5["스테이션 회피"]
    
    style P1 fill:#ff0000,color:#fff
    style P2 fill:#ff6b6b,color:#fff
    style P3 fill:#ffd43b,color:#000
    style P4 fill:#74c0fc,color:#fff
    style P5 fill:#b2f2bb,color:#000
```
