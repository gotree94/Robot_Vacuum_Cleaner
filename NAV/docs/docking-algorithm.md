# 🎯 도킹 알고리즘 상세 순서도

> **도킹 방식**: 정면 도킹 (Front-First Docking)
> - 먼지통이 후면에 위치
> - 로봇 전면으로 스테이션에 진입하여 충전 단자 접촉
> - 자동 비움 스테이션의 경우, 도킹 후 후면 먼지통이 흡입구와 연결

## 1. 전체 도킹 프로세스

```mermaid
stateDiagram-v2
    [*] --> Cleaning: 청소 중
    
    Cleaning --> BatteryCheck: 주기적 체크
    BatteryCheck --> Cleaning: 배터리 OK
    BatteryCheck --> DockingMode: 배터리 < 20%
    
    DockingMode --> Phase1_Search: 도킹 모드 진입
    
    state Phase1_Search {
        [*] --> WallFollow
        WallFollow --> ForceFieldDetect: Far L/R 빔 탐색
        ForceFieldDetect --> DirectionTurn: Force Field 감지
        DirectionTurn --> [*]
    }
    
    Phase1_Search --> Phase2_Approach
    
    state Phase2_Approach {
        [*] --> FrontBeamDetect
        FrontBeamDetect --> LeftOnly: Front-L만 감지
        FrontBeamDetect --> RightOnly: Front-R만 감지
        FrontBeamDetect --> BothBeams: 양쪽 감지
        LeftOnly --> MicroRight: 미세 우회전
        RightOnly --> MicroLeft: 미세 좌회전
        MicroRight --> FrontBeamDetect
        MicroLeft --> FrontBeamDetect
        BothBeams --> OverlapZone
        OverlapZone --> [*]
    }
    
    Phase2_Approach --> Phase3_Align
    
    state Phase3_Align {
        [*] --> CenterBeamSearch
        CenterBeamSearch --> FineAlign: Center 빔 감지
        FineAlign --> SignalCompare: 전면 RX×2 비교
        SignalCompare --> LeftStronger: L > R
        SignalCompare --> RightStronger: L < R
        SignalCompare --> Balanced: L ≈ R
        LeftStronger --> MicroAdjustR
        RightStronger --> MicroAdjustL
        MicroAdjustR --> SignalCompare
        MicroAdjustL --> SignalCompare
        Balanced --> [*]
    }
    
    Phase3_Align --> Phase4_Dock
    
    state Phase4_Dock {
        [*] --> SlowForward
        SlowForward --> ContactCheck
        ContactCheck --> VoltageDetect: 접촉 성공
        ContactCheck --> AlignCheck: 접촉 실패
        AlignCheck --> SlowForward: 정렬 OK
        AlignCheck --> Phase3_Align: 정렬 이탈
        VoltageDetect --> MotorStop: 전압 OK
        VoltageDetect --> Retry: 전압 이상
        Retry --> Phase3_Align
        MotorStop --> [*]
    }
    
    Phase4_Dock --> Charging
    Charging --> [*]: 충전 완료
```

## 2. 위치별 접근 시나리오 상태도

```mermaid
stateDiagram-v2
    [*] --> PositionAnalysis
    
    state PositionAnalysis {
        [*] --> ScanBeams
        ScanBeams --> LeftApproach: Far-R 감지
        ScanBeams --> RightApproach: Far-L 감지
        ScanBeams --> FrontApproach: Front L+R 감지
        ScanBeams --> RearApproach: 후면 RX 감지
    }
    
    state LeftApproach {
        [*] --> TurnLeft_LA
        TurnLeft_LA --> ForwardL
        ForwardL --> FrontR_Entry
        FrontR_Entry --> OverlapL
        OverlapL --> [*]
    }
    
    state RightApproach {
        [*] --> TurnRight_RA
        TurnRight_RA --> ForwardR
        ForwardR --> FrontL_Entry
        FrontL_Entry --> OverlapR
        OverlapR --> [*]
    }
    
    state FrontApproach {
        [*] --> CheckSkew
        CheckSkew --> SkewLeft: Front-L만 감지
        CheckSkew --> SkewRight: Front-R만 감지
        CheckSkew --> Centered: 양쪽 균등
        SkewLeft --> CorrectRight
        SkewRight --> CorrectLeft
        CorrectRight --> CheckSkew
        CorrectLeft --> CheckSkew
        Centered --> [*]
    }
    
    state RearApproach {
        [*] --> Turn180
        Turn180 --> FrontNow: 정면 도킹 준비
        FrontNow --> [*]
        note right of Turn180 : 정면 도킹만 지원\n후면 도킹 불가
    }
    
    LeftApproach --> CenterAlign
    RightApproach --> CenterAlign
    FrontApproach --> CenterAlign
    RearApproach --> FrontApproach
    
    CenterAlign --> Docking
    Docking --> [*]
```

## 3. 센서 신호 처리 흐름

```mermaid
flowchart TB
    subgraph SENSORS["📡 IR 센서 입력"]
        OMNI["Omni-RX<br/>(도킹 탐색)"]
        DIR_FRONT["Dir-RX 전면×2<br/>(정밀 정렬)"]
        DIR_120["Dir-RX ±120°<br/>(광역 감지)"]
        DIR_REAR["Dir-RX 후면<br/>(Virtual Wall/<br/>후진 충돌 방지)"]
    end
    
    subgraph PROCESSING["🔧 신호 처리"]
        DECODE["빔 코드 디코딩<br/>(채널 식별)"]
        STRENGTH["신호 강도 측정<br/>(ADC)"]
        COMPARE["좌/우 비교<br/>(정렬 판단)"]
    end
    
    subgraph DECISION["🧠 의사결정"]
        PHASE_DET["현재 Phase 판단"]
        ACTION_SEL["동작 선택"]
    end
    
    subgraph OUTPUT["⚙️ 모터 제어"]
        LEFT_MOTOR["좌측 모터"]
        RIGHT_MOTOR["우측 모터"]
    end
    
    OMNI --> DECODE
    DIR_FRONT --> STRENGTH
    DIR_120 --> DECODE
    DIR_REAR --> DECODE
    
    DECODE --> PHASE_DET
    STRENGTH --> COMPARE
    COMPARE --> ACTION_SEL
    PHASE_DET --> ACTION_SEL
    
    ACTION_SEL --> LEFT_MOTOR
    ACTION_SEL --> RIGHT_MOTOR
```

## 4. 에러 처리 및 재시도

```mermaid
flowchart TD
    DOCK_ATTEMPT["도킹 시도"] --> SUCCESS{성공?}
    
    SUCCESS -->|Yes| CHARGING["충전 시작"]
    SUCCESS -->|No| ERROR_TYPE{에러 유형?}
    
    ERROR_TYPE -->|"정렬 이탈"| REALIGN["재정렬"]
    ERROR_TYPE -->|"접촉 실패"| RETRY_CONTACT["후진 → 재접근"]
    ERROR_TYPE -->|"전압 이상"| CHECK_CONTACT["단자 상태 확인"]
    ERROR_TYPE -->|"신호 손실"| RESTART_SEARCH["탐색 재시작"]
    
    REALIGN --> RETRY_COUNT{재시도<br/>횟수?}
    RETRY_CONTACT --> RETRY_COUNT
    CHECK_CONTACT --> RETRY_COUNT
    RESTART_SEARCH --> RETRY_COUNT
    
    RETRY_COUNT -->|"< 3회"| DOCK_ATTEMPT
    RETRY_COUNT -->|"≥ 3회"| FALLBACK["폴백 모드"]
    
    FALLBACK --> WALL_FOLLOW["벽 따라가기로<br/>재탐색"]
    WALL_FOLLOW --> DOCK_ATTEMPT
    
    style ERROR_TYPE fill:#ffa94d
    style FALLBACK fill:#ff6b6b,color:#fff
```

## 5. 도킹 완료 후 시퀀스 (자동 비움 스테이션)

```mermaid
flowchart TD
    DOCKED["✅ 정면 도킹 완료"] --> CONTACT_CHECK{충전 단자<br/>접촉 확인?}
    
    CONTACT_CHECK -->|Yes| CHARGING_START["🔋 충전 시작"]
    CONTACT_CHECK -->|No| RETRY["재도킹 시도"]
    
    CHARGING_START --> DUST_CHECK{먼지통<br/>비움 필요?}
    
    DUST_CHECK -->|No| CHARGE_ONLY["충전만 진행"]
    DUST_CHECK -->|Yes| EMPTY_SEQ["🗑️ 자동 비움 시퀀스"]
    
    subgraph EMPTY_SEQUENCE["자동 비움 프로세스"]
        EMPTY_SEQ --> DOOR_OPEN["먼지통 도어 열림"]
        DOOR_OPEN --> VACUUM_ON["스테이션 흡입 모터 ON"]
        VACUUM_ON --> WAIT_EMPTY["비움 대기 (10-30초)"]
        WAIT_EMPTY --> VACUUM_OFF["흡입 모터 OFF"]
        VACUUM_OFF --> DOOR_CLOSE["먼지통 도어 닫힘"]
    end
    
    DOOR_CLOSE --> CHARGE_CONTINUE["충전 계속"]
    CHARGE_ONLY --> CHARGE_DONE{충전 완료?}
    CHARGE_CONTINUE --> CHARGE_DONE
    
    CHARGE_DONE -->|No| CHARGE_CONTINUE
    CHARGE_DONE -->|Yes| STANDBY["대기 모드"]
    
    STANDBY --> NEXT_CLEAN{청소 예약?}
    NEXT_CLEAN -->|Yes| UNDOCK["도킹 해제 → 청소 시작"]
    NEXT_CLEAN -->|No| STANDBY
    
    style DOCKED fill:#51cf66,color:#fff
    style EMPTY_SEQ fill:#ffd43b,color:#000
```

### 도킹 구조 (정면 도킹 + 후면 먼지통)

```
        ┌─────────────────────────────┐
        │      Auto-Empty Station      │
        │  ┌─────────────────────┐    │
        │  │    흡입구 (상단)     │◀───┼── 로봇 후면 (먼지통) 연결
        │  └─────────────────────┘    │
        │                             │
        │    ┌───┐       ┌───┐       │
        │    │ L │       │ R │       │◀── 충전 단자
        │    └───┘       └───┘       │
        │         IR Beams            │
        └──────────┬──────────────────┘
                   │
                   ▼
            ┌─────────────┐
            │  🤖 Robot   │
            │ ┌─────────┐ │
            │ │ 전면    │ │◀── 충전 접점
            │ │ (Front) │ │
            │ └─────────┘ │
            │             │
            │ ┌─────────┐ │
            │ │ 먼지통  │ │◀── 후면 (흡입구와 연결)
            │ │ (Rear)  │ │
            │ └─────────┘ │
            └─────────────┘
```
