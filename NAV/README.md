# 🤖 로봇 청소기 IR 네비게이션 시스템 분석

로봇 청소기의 적외선(IR) 기반 네비게이션 시스템을 분석한 문서입니다. 충전 스테이션 도킹 유도와 장애물 회피 기능의 원리와 구현 방법을 다룹니다.

## 📋 목차

- [1. 시스템 개요](#1-시스템-개요)
- [2. 주요 부품 목록](#2-주요-부품-목록)
- [3. 도킹 알고리즘](#3-도킹-알고리즘)
- [4. 장애물 회피 시스템](#4-장애물-회피-시스템)
- [5. 참고 자료](#5-참고-자료)

---

## 1. 시스템 개요

### 1.1 충전 스테이션 (Docking Station)

<!-- 실제 사진을 여기에 추가하세요 -->
![충전 스테이션 상단](./images/docking_station_upper.jpg)
![충전 스테이션 하단](./images/docking_station_lower.jpg)

### 1.2 로봇 본체 (Robot Body)

<!-- 실제 사진을 여기에 추가하세요 -->
![로봇 범퍼 IR 센서](./images/robot_bumper_ir.jpg)
![로봇 IR 수신기](./images/robot_ir_receiver.jpg)

### 1.3 기능별 역할 분석

#### 🔴 충전 스테이션 IR LED (송신)

| 위치 | 구성 | 기능 |
|------|------|------|
| **상단 Blue LED** | 좌우 대칭 4개, 곡면 렌즈 | 상태 표시 (충전중/대기) |
| **상단 평면 IR LED** | 좌우 끝, 평평한 면 | 근접 회피 신호 (Omni-directional Force Field) |
| **하단 IR LED** | SMD 타입 5개 | 도킹 유도 빔 (방향성 코딩된 신호) |

**하단 IR LED 상세 구성:**
- **Far L/R** (±30° 방향): Force Field - 청소 중 스테이션 회피용
- **Front L/R** (정면 좌우): 좌우 정렬 빔 - Overlapping Field 형성
- **Center** (정중앙): 정밀 도킹 빔 - Home Beam

> **참고**: 먼지통이 후면에 위치하며, 로봇은 **정면으로 도킹**합니다. 
> 자동 비움 스테이션의 경우 도킹 후 후면 먼지통이 흡입구와 연결됩니다.

#### 🔵 로봇 본체 IR 센서

| 위치 | 구성 | 기능 |
|------|------|------|
| **범퍼 IR TX** | SMD LED × 20개 | 장애물 감지용 (반사 방식, 38kHz 변조) |
| **전면 IR RX ×2** | 정면 중앙, 근접 배치 | 도킹 빔 수신 (정밀 정렬) |
| **전면 ±120° IR RX** | 좌우 대칭 | 광역 도킹 신호 탐지 |
| **후면 ±120° IR RX** | 뒷면 좌우 각 1개 | Virtual Wall 감지 / 후진 시 충돌 방지 |

---

## 2. 주요 부품 목록

### 2.1 충전 스테이션 BOM

| Ref | Part Number | Description | Qty |
|-----|-------------|-------------|-----|
| U1 | 7805 | 5V LDO Regulator | 1 |
| U3 | S033 PHVG 825Y | IR Controller/Timer IC | 1 |
| Q1-Q15 | HY3D | N-ch MOSFET (IR LED Driver) | 15 |
| D1 | SS24 | 2A Schottky Diode | 1 |
| D2 | MCC ME | Rectifier Diode | 1 |
| C1 | 100µF 35V | Electrolytic Capacitor | 1 |
| LED1-5 | - | Status Indicator (Blue/Green) | 5 |
| IR LED | 940nm SMD | Docking Beacon Emitter | 5 |
| TP1-13 | - | Test Points | 13 |

### 2.2 로봇 본체 BOM

| Ref | Part Number | Description | Qty |
|-----|-------------|-------------|-----|
| MCU | STM32F103C8T6 | Main Controller (ARM Cortex-M3) | 1 |
| IR TX | 940nm SMD LED | Obstacle Detection Emitter | 20 |
| Omni-RX | Dome Type IR Receiver | Docking Signal Receiver | 1 |
| Dir-RX | TSOP38238 / VS1838B | Directional IR Receiver | 6 |
| Obst-RX | TSOP38238 | Obstacle Detection Receiver | N |
| Driver | 74HC595 / ULN2803 | LED Array Driver | 3 |
| OSC | NE555 (Optional) | 38kHz Oscillator | 1 |
| Motor Driver | L298N | Dual H-Bridge | 1 |

### 2.3 공통 사양

| Parameter | Value | Note |
|-----------|-------|------|
| IR 캐리어 주파수 | 38kHz ±1kHz | TSOP38238 최적 감도 |
| IR 파장 | 940nm | 근적외선 |
| 장애물 감지 범위 | 2cm ~ 40cm | 가변저항으로 조절 |
| 빔 필드 각도 | 45° ~ 90° | Front L/R Overlap |

---

## 3. 도킹 알고리즘

### 3.1 도킹 시나리오 개요

```mermaid
flowchart TB
    subgraph SCENARIOS["🎯 도킹 시나리오"]
        S1["🔋 배터리 Low<br/>도킹 필요"]
        S2["🧹 청소 중<br/>스테이션 통과"]
        S3["📍 위치별 접근<br/>좌/우/정면"]
    end
    
    S1 --> DOCK_ALGO
    S2 --> PASS_ALGO
    S3 --> DOCK_ALGO
    
    subgraph DOCK_ALGO["도킹 알고리즘"]
        D1[Phase 1: 탐색]
        D2[Phase 2: 접근]
        D3[Phase 3: 정렬]
        D4[Phase 4: 도킹]
    end
    
    subgraph PASS_ALGO["통과 알고리즘"]
        P1[Force Field 감지]
        P2[회피 기동]
        P3[청소 재개]
    end
```

### 3.2 배터리 Low → 도킹 복귀 (메인 알고리즘)

```mermaid
flowchart TD
    START((🔋 배터리 Low)) --> CHECK_LEVEL{배터리<br/>< 20%?}
    CHECK_LEVEL -->|No| CONTINUE[청소 계속]
    CHECK_LEVEL -->|Yes| DOCK_MODE[/"⚡ 도킹 모드 진입"/]
    
    DOCK_MODE --> WALL_FOLLOW["🧱 벽 따라가기 시작"]
    WALL_FOLLOW --> SCAN_FF{Force Field<br/>감지?}
    
    SCAN_FF -->|No| WALL_FOLLOW
    SCAN_FF -->|Yes| DETECT_DIR["📡 Far L/R 빔 감지"]
    
    DETECT_DIR --> WHICH_FAR{어느 빔?}
    WHICH_FAR -->|Far-L 감지| TURN_RIGHT["↻ 우회전"]
    WHICH_FAR -->|Far-R 감지| TURN_LEFT["↺ 좌회전"]
    WHICH_FAR -->|Both| APPROACH["⬆️ 직진 접근"]
    
    TURN_RIGHT --> APPROACH
    TURN_LEFT --> APPROACH
    
    APPROACH --> PHASE2["🎯 Phase 2: 접근"]
    
    subgraph PHASE2_DETAIL["Phase 2: Front L/R 빔 정렬"]
        PHASE2 --> DETECT_FRONT{Front 빔<br/>감지?}
        DETECT_FRONT -->|Front-L only| ADJ_RIGHT["미세 우회전"]
        DETECT_FRONT -->|Front-R only| ADJ_LEFT["미세 좌회전"]
        DETECT_FRONT -->|Both<br/>Overlap Zone| CENTER_SEARCH["중심선 탐색"]
        ADJ_RIGHT --> DETECT_FRONT
        ADJ_LEFT --> DETECT_FRONT
    end
    
    CENTER_SEARCH --> PHASE3["🔍 Phase 3: 정렬"]
    
    subgraph PHASE3_DETAIL["Phase 3: Center 빔 정렬"]
        PHASE3 --> DETECT_CENTER{Center 빔<br/>감지?}
        DETECT_CENTER -->|No| CENTER_SEARCH
        DETECT_CENTER -->|Yes| FINE_ALIGN["전면 RX×2 신호 비교"]
        FINE_ALIGN --> SIGNAL_BALANCE{신호 강도<br/>균등?}
        SIGNAL_BALANCE -->|L > R| MICRO_RIGHT["미세 우측 보정"]
        SIGNAL_BALANCE -->|L < R| MICRO_LEFT["미세 좌측 보정"]
        SIGNAL_BALANCE -->|L ≈ R| STRAIGHT["✅ 정렬 완료"]
        MICRO_RIGHT --> FINE_ALIGN
        MICRO_LEFT --> FINE_ALIGN
    end
    
    STRAIGHT --> PHASE4["🔌 Phase 4: 도킹"]
    
    subgraph PHASE4_DETAIL["Phase 4: 최종 도킹"]
        PHASE4 --> SLOW_FWD["저속 직진"]
        SLOW_FWD --> CONTACT{충전 단자<br/>접촉?}
        CONTACT -->|No| CHECK_ALIGN{정렬 유지?}
        CHECK_ALIGN -->|No| FINE_ALIGN
        CHECK_ALIGN -->|Yes| SLOW_FWD
        CONTACT -->|Yes| VOLTAGE_CHECK{전압 감지?}
        VOLTAGE_CHECK -->|No| RETRY["후진 → 재시도"]
        RETRY --> PHASE3
        VOLTAGE_CHECK -->|Yes| MOTOR_STOP["모터 정지"]
    end
    
    MOTOR_STOP --> CHARGING((🔋 충전 시작))
    
    style START fill:#ff6b6b,color:#fff
    style CHARGING fill:#51cf66,color:#fff
    style DOCK_MODE fill:#ffd43b,color:#000
```

### 3.3 청소 중 스테이션 통과 시나리오

```mermaid
flowchart TD
    CLEAN_START((🧹 청소 중)) --> MOVE["이동 중"]
    
    MOVE --> DETECT_FORCE{Force Field<br/>감지?}
    DETECT_FORCE -->|No| MOVE
    DETECT_FORCE -->|Yes| CHECK_MODE{도킹 모드?}
    
    CHECK_MODE -->|Yes| CONTINUE_DOCK["도킹 알고리즘 계속"]
    CHECK_MODE -->|No| AVOID_STATION["⚠️ 스테이션 회피"]
    
    subgraph AVOIDANCE["스테이션 회피 기동"]
        AVOID_STATION --> GET_DIRECTION{접근 방향?}
        
        GET_DIRECTION -->|정면 접근| TURN_180["↻ 180° 회전"]
        GET_DIRECTION -->|좌측 접근| TURN_R90["↻ 90° 우회전"]
        GET_DIRECTION -->|우측 접근| TURN_L90["↺ 90° 좌회전"]
        
        TURN_180 --> MOVE_AWAY["스테이션에서 이탈"]
        TURN_R90 --> MOVE_AWAY
        TURN_L90 --> MOVE_AWAY
    end
    
    MOVE_AWAY --> RESUME["청소 재개"]
    RESUME --> MOVE
    
    style CLEAN_START fill:#74c0fc,color:#fff
    style AVOID_STATION fill:#ffa94d,color:#000
```

### 3.4 위치별 도킹 접근 시나리오

#### Case 1: 스테이션 왼쪽에서 접근

```mermaid
flowchart LR
    subgraph POSITION["🗺️ 로봇 위치: 스테이션 왼쪽"]
        ROBOT["🤖"]
        STATION["🔌 Station"]
    end
    
    ROBOT -->|"Far-R 빔 감지"| DETECT
    
    DETECT["Far-R 감지"] --> TURN["↺ 좌회전<br/>(스테이션 방향)"]
    TURN --> APPROACH["직진 접근"]
    APPROACH --> FRONT_R["Front-R 빔 진입"]
    FRONT_R --> OVERLAP["Overlap Zone 진입"]
    OVERLAP --> CENTER["Center 빔 정렬"]
    CENTER --> DOCK["✅ 도킹"]
    
    style ROBOT fill:#74c0fc,color:#fff
    style STATION fill:#ff6b6b,color:#fff
```

#### Case 2: 스테이션 오른쪽에서 접근

```mermaid
flowchart RL
    subgraph POSITION["🗺️ 로봇 위치: 스테이션 오른쪽"]
        STATION["🔌 Station"]
        ROBOT["🤖"]
    end
    
    ROBOT -->|"Far-L 빔 감지"| DETECT
    
    DETECT["Far-L 감지"] --> TURN["↻ 우회전<br/>(스테이션 방향)"]
    TURN --> APPROACH["직진 접근"]
    APPROACH --> FRONT_L["Front-L 빔 진입"]
    FRONT_L --> OVERLAP["Overlap Zone 진입"]
    OVERLAP --> CENTER["Center 빔 정렬"]
    CENTER --> DOCK["✅ 도킹"]
    
    style ROBOT fill:#74c0fc,color:#fff
    style STATION fill:#ff6b6b,color:#fff
```

#### Case 3: 스테이션 정면에서 접근 (좌측으로 틀어짐)

```mermaid
flowchart TD
    subgraph POSITION["🗺️ 로봇: 정면, 좌측으로 틀어짐"]
        direction TB
        STATION["🔌 Station"]
        ROBOT["🤖 ↖️"]
    end
    
    ROBOT -->|"Front-L만 감지<br/>Front-R 미감지"| DETECT
    
    DETECT["Front-L only"] --> PROBLEM["❌ 좌측으로 치우침"]
    PROBLEM --> CORRECT["↻ 미세 우회전"]
    CORRECT --> RECHECK{Front-R<br/>감지?}
    RECHECK -->|No| CORRECT
    RECHECK -->|Yes| OVERLAP["✅ Overlap Zone 진입"]
    OVERLAP --> CENTER["Center 빔 정렬"]
    CENTER --> FINE["전면 RX×2 균등화"]
    FINE --> DOCK["✅ 도킹"]
    
    style ROBOT fill:#74c0fc,color:#fff
    style STATION fill:#ff6b6b,color:#fff
    style PROBLEM fill:#ffa94d,color:#000
```

#### Case 4: 스테이션 정면에서 접근 (우측으로 틀어짐)

```mermaid
flowchart TD
    subgraph POSITION["🗺️ 로봇: 정면, 우측으로 틀어짐"]
        direction TB
        STATION["🔌 Station"]
        ROBOT["🤖 ↗️"]
    end
    
    ROBOT -->|"Front-R만 감지<br/>Front-L 미감지"| DETECT
    
    DETECT["Front-R only"] --> PROBLEM["❌ 우측으로 치우침"]
    PROBLEM --> CORRECT["↺ 미세 좌회전"]
    CORRECT --> RECHECK{Front-L<br/>감지?}
    RECHECK -->|No| CORRECT
    RECHECK -->|Yes| OVERLAP["✅ Overlap Zone 진입"]
    OVERLAP --> CENTER["Center 빔 정렬"]
    CENTER --> FINE["전면 RX×2 균등화"]
    FINE --> DOCK["✅ 도킹"]
    
    style ROBOT fill:#74c0fc,color:#fff
    style STATION fill:#ff6b6b,color:#fff
    style PROBLEM fill:#ffa94d,color:#000
```

#### Case 5: 후면이 스테이션을 향할 때 (180° 회전 후 정면 도킹)

```mermaid
flowchart TD
    START["🤖 후면이 스테이션 방향"] --> REAR_DETECT{후면 RX로<br/>신호 감지?}
    
    REAR_DETECT -->|Yes| TURN_180["↻ 180° 회전<br/>(정면 도킹 준비)"]
    REAR_DETECT -->|No| SEARCH["탐색 모드"]
    
    TURN_180 --> FRONT_NOW["전면이 스테이션 방향"]
    FRONT_NOW --> NORMAL_DOCK["정면 도킹 알고리즘"]
    
    SEARCH --> WALL_FOLLOW["벽 따라가기"]
    WALL_FOLLOW --> NORMAL_DOCK
    
    NORMAL_DOCK --> DOCK["✅ 정면 도킹 완료"]
    
    style START fill:#74c0fc,color:#fff
```

> **Note**: 이 로봇은 **정면 도킹만 지원**합니다. 후면에 먼지통이 있어 역방향 도킹은 불가능하며, 
> 후면 IR RX는 Virtual Wall 감지 및 후진 시 충돌 방지 용도로 사용됩니다.

### 3.5 도킹 빔 필드 다이어그램

> **도킹 방식**: 정면 도킹 (Front-First Docking)
> - 로봇 전면의 충전 단자가 스테이션과 접촉
> - 먼지통(후면)은 자동 비움 스테이션의 흡입구와 연결

```
                    ┌─────────────┐
                    │   Station   │
                    └──────┬──────┘
                           │
            Far-L    Front-L│Front-R    Far-R
              ╲        ╲    │    ╱        ╱
               ╲        ╲   │   ╱        ╱
                ╲    ────┼───────    ╱
                 ╲  ╱    │Center╲  ╱
                  ╲╱     │       ╲╱
                   ╲     │       ╱
                    ╲    │      ╱
                     ╲   │     ╱
              Force   ╲  │    ╱   Force
              Field    ╲ │   ╱    Field
               (회피)   ╲│  ╱     (회피)
                        ╲│ ╱
                    ┌────┴────┐
                    │ Overlap │ ← 정렬 구간
                    │  Zone   │
                    └─────────┘
                         │
                         ▼
                    [도킹 경로]
```

---

## 4. 장애물 회피 시스템

### 4.1 IR 센서 사양

#### 송신부 (TX LED)

| Parameter | Value |
|-----------|-------|
| 파장 | 940nm (근적외선) |
| 구동 주파수 | 38kHz PWM 변조 |
| 구동 전류 | 20~100mA (거리에 따라 조절) |
| 빔 각도 | 20°~30° (SMD 타입) |
| 배치 | 범퍼 전면 20개 (순차 스캔) |

#### 수신부 (IR Receiver)

| Parameter | Value |
|-----------|-------|
| 호환 IC | TSOP38238 / VS1838B |
| 수신 파장 | 940nm ±50nm |
| 중심 주파수 | 38kHz |
| 특징 | AGC (Auto Gain Control) 내장 |
| 출력 방식 | Active Low (감지 시 LOW) |

#### 감지 원리

```
    ┌─────────┐
    │ IR TX   │ ────── 38kHz 변조 신호 ──────▶ ┌──────────┐
    │  LED    │                                │  장애물   │
    └─────────┘                                │          │
                                               └────┬─────┘
    ┌─────────┐                                     │
    │ IR RX   │ ◀────── 반사 신호 ──────────────────┘
    │ Sensor  │
    └─────────┘
    
    감지 거리 = f(반사 신호 강도)
    유효 범위: 2cm ~ 40cm
```

### 4.2 장애물 회피 메인 알고리즘

```mermaid
flowchart TD
    START((🧹 청소 중)) --> SCAN["IR TX 순차 스캔<br/>(20채널 멀티플렉싱)"]
    
    SCAN --> DETECT{장애물<br/>감지?}
    DETECT -->|No| MOVE["직진 이동"]
    MOVE --> SCAN
    
    DETECT -->|Yes| ANALYZE["감지 채널 분석"]
    
    ANALYZE --> POSITION{감지 위치?}
    
    POSITION -->|"정면 (Ch 9-12)"| FRONT_OBS["🚧 정면 장애물"]
    POSITION -->|"좌측 (Ch 1-8)"| LEFT_OBS["🚧 좌측 장애물"]
    POSITION -->|"우측 (Ch 13-20)"| RIGHT_OBS["🚧 우측 장애물"]
    POSITION -->|"전방위"| MULTI_OBS["🚧 복합 장애물"]
    
    FRONT_OBS --> FRONT_ACTION
    LEFT_OBS --> LEFT_ACTION
    RIGHT_OBS --> RIGHT_ACTION
    MULTI_OBS --> MULTI_ACTION
    
    subgraph FRONT_ACTION["정면 장애물 회피"]
        F1["정지"] --> F2["후진 5cm"]
        F2 --> F3{좌/우<br/>공간 확인}
        F3 -->|좌측 여유| F4L["↺ 90° 좌회전"]
        F3 -->|우측 여유| F4R["↻ 90° 우회전"]
        F3 -->|양쪽 막힘| F5["180° 회전"]
    end
    
    subgraph LEFT_ACTION["좌측 장애물 회피"]
        L1["감속"] --> L2["↻ 우측으로 조향"]
        L2 --> L3["장애물 따라가기<br/>(벽 청소 모드)"]
    end
    
    subgraph RIGHT_ACTION["우측 장애물 회피"]
        R1["감속"] --> R2["↺ 좌측으로 조향"]
        R2 --> R3["장애물 따라가기<br/>(벽 청소 모드)"]
    end
    
    subgraph MULTI_ACTION["복합 장애물 회피"]
        M1["정지"] --> M2["최소 감지 방향 확인"]
        M2 --> M3["해당 방향으로 회전"]
        M3 --> M4["탈출 경로 탐색"]
    end
    
    F4L --> RESUME["청소 재개"]
    F4R --> RESUME
    F5 --> RESUME
    L3 --> RESUME
    R3 --> RESUME
    M4 --> RESUME
    
    RESUME --> SCAN
    
    style START fill:#74c0fc,color:#fff
    style FRONT_OBS fill:#ff6b6b,color:#fff
    style LEFT_OBS fill:#ffd43b,color:#000
    style RIGHT_OBS fill:#ffd43b,color:#000
    style MULTI_OBS fill:#ff922b,color:#fff
```

### 4.3 시나리오별 장애물 회피

#### Scenario 1: 정면 벽 감지

```mermaid
flowchart LR
    subgraph BEFORE["감지 전"]
        R1["🤖 →"]
        W1["┃ 벽"]
    end
    
    R1 -->|"Ch 9-12<br/>HIGH → LOW"| DETECT["🚨 정면 감지"]
    
    DETECT --> STOP["정지"]
    STOP --> BACK["후진 5cm"]
    BACK --> TURN["90° 회전"]
    TURN --> WALL_FOLLOW["벽 따라가기"]
    
    subgraph AFTER["회피 후"]
        R2["🤖 ↑"]
        W2["━━ 벽"]
    end
    
    WALL_FOLLOW --> R2
```

#### Scenario 2: 좌측 장애물 (가구 다리 등)

```mermaid
flowchart TD
    subgraph SITUATION["상황: 좌측 가구 다리"]
        OBS["🪑"]
        ROBOT["🤖 →"]
    end
    
    ROBOT -->|"Ch 3-6<br/>감지"| DETECT["🚨 좌측 장애물"]
    
    DETECT --> SLOW["감속"]
    SLOW --> STEER["우측 조향 (+15°)"]
    STEER --> CHECK{클리어?}
    CHECK -->|No| STEER
    CHECK -->|Yes| RESUME["정상 주행"]
    
    style OBS fill:#d4a373,color:#fff
```

#### Scenario 3: 우측 장애물

```mermaid
flowchart TD
    subgraph SITUATION["상황: 우측 장애물"]
        ROBOT["🤖 →"]
        OBS["📦"]
    end
    
    ROBOT -->|"Ch 14-17<br/>감지"| DETECT["🚨 우측 장애물"]
    
    DETECT --> SLOW["감속"]
    SLOW --> STEER["좌측 조향 (-15°)"]
    STEER --> CHECK{클리어?}
    CHECK -->|No| STEER
    CHECK -->|Yes| RESUME["정상 주행"]
    
    style OBS fill:#8b5a2b,color:#fff
```

#### Scenario 4: 코너 진입 (양측 장애물)

```mermaid
flowchart TD
    subgraph CORNER["코너 상황"]
        W1["┃"]
        ROBOT["🤖"]
        W2["━━"]
    end
    
    ROBOT -->|"Ch 1-4 + Ch 9-12<br/>동시 감지"| DETECT["🚨 코너 감지"]
    
    DETECT --> ANALYZE["감지 패턴 분석"]
    ANALYZE --> CORNER_TYPE{코너 유형?}
    
    CORNER_TYPE -->|"ㄱ자 코너"| RIGHT_TURN["↻ 90° 우회전"]
    CORNER_TYPE -->|"ㄴ자 코너"| LEFT_TURN["↺ 90° 좌회전"]
    
    RIGHT_TURN --> EDGE_CLEAN["코너 청소"]
    LEFT_TURN --> EDGE_CLEAN
    
    EDGE_CLEAN --> EXIT["코너 탈출"]
```

#### Scenario 5: 낭떠러지 감지 (계단 등)

```mermaid
flowchart TD
    START["🤖 이동 중"] --> CLIFF_SENSOR{바닥 IR<br/>반사 없음?}
    
    CLIFF_SENSOR -->|"반사 신호 약함<br/>(바닥 없음)"| CLIFF["⚠️ 낭떠러지 감지!"]
    CLIFF_SENSOR -->|정상 반사| CONTINUE["계속 이동"]
    
    CLIFF --> EMERGENCY["🛑 긴급 정지"]
    EMERGENCY --> BACKUP["후진 10cm"]
    BACKUP --> TURN_AWAY["180° 회전"]
    TURN_AWAY --> SAFE["안전 구역 이동"]
    
    CONTINUE --> START
    SAFE --> START
    
    style CLIFF fill:#ff6b6b,color:#fff
    style EMERGENCY fill:#ff0000,color:#fff
```

#### Scenario 6: 이동 중인 장애물 (사람, 반려동물)

```mermaid
flowchart TD
    SCAN["IR 스캔"] --> DETECT{장애물<br/>감지?}
    
    DETECT -->|Yes| MEASURE["거리 측정"]
    DETECT -->|No| SCAN
    
    MEASURE --> TREND{거리 변화<br/>추세?}
    
    TREND -->|"거리 감소<br/>(접근 중)"| DYNAMIC["🏃 동적 장애물"]
    TREND -->|"거리 일정"| STATIC["🪨 정적 장애물"]
    
    DYNAMIC --> WAIT["정지 & 대기<br/>(3초)"]
    WAIT --> RECHECK{장애물<br/>사라짐?}
    RECHECK -->|Yes| RESUME["주행 재개"]
    RECHECK -->|No| AVOID["우회 경로 탐색"]
    
    STATIC --> NORMAL_AVOID["일반 회피 루틴"]
    
    AVOID --> RESUME
    NORMAL_AVOID --> RESUME
    RESUME --> SCAN
    
    style DYNAMIC fill:#ffd43b,color:#000
```

### 4.4 센서 채널 맵핑

```
              전면
        ┌─────────────────┐
        │  9  10  11  12  │  ← 정면 감지
       ╱│ 8            13 │╲
      ╱ │ 7            14 │ ╲
     │  │ 6            15 │  │
     │  │ 5            16 │  │
      ╲ │ 4            17 │ ╱
       ╲│ 3            18 │╱
        │ 2            19 │
        │ 1            20 │
        └─────────────────┘
              후면
              
    Ch 1-8:   좌측 감지
    Ch 9-12:  정면 감지  
    Ch 13-20: 우측 감지
```

---

## 5. 참고 자료

### 특허 문서

| Patent No. | Title | Owner |
|------------|-------|-------|
| US8380350B2 | Autonomous coverage robot navigation system | iRobot |
| US20120323365A1 | Docking process for recharging an autonomous mobile device | Microsoft |
| US8311674B2 | Robotic vacuum cleaner | Samsung |
| US20140100693A1 | Robot management systems for determining docking station pose | iRobot |

### 기술 문서

- [TSOP38238 Datasheet](https://www.vishay.com/docs/82459/tsop382.pdf)
- [iRobot Virtual Wall Lighthouse Overview](https://homesupport.irobot.com/)
- [IR Obstacle Avoidance Sensor Module](https://protosupplies.com/product/ir-obstacle-avoidance-sensor-module/)

---

## 📄 라이선스

이 문서는 교육 및 연구 목적으로 작성되었습니다.

---

*Last Updated: 2025.01*
