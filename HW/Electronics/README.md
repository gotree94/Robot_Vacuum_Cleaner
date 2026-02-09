# BL520 Charger Board V1.0 - EDA Files

## 개요

로봇 청소기 충전 스테이션 (BL520 Charger Board)의 역설계 회로도 파일입니다.
세 가지 방식으로 생성되었습니다.

---

## 파일 구조

```
EDA_Files/
├── KiCad/                          # KiCad 8.0 직접 작성
│   ├── BL520_Charger.kicad_pro     # 프로젝트 파일
│   └── BL520_Charger.kicad_sch     # 회로도 파일
│
├── OrCAD_TCL/                      # OrCAD Capture TCL 스크립트
│   └── BL520_Charger.tcl           # TCL 스크립트
│
└── KiCad_Python/                   # KiCad Python API 스크립트
    ├── BL520_kicad_generator.py    # Python 생성 스크립트
    ├── BL520_Charger_generated.kicad_sch  # 생성된 회로도
    ├── BL520_BOM_generated.md      # 생성된 BOM
    └── BL520_Netlist_generated.txt # 생성된 넷리스트
```

---

## 1. KiCad 8.0 (직접 작성)

### 사용 방법
1. KiCad 8.0 이상 설치
2. `BL520_Charger.kicad_pro` 파일 열기
3. 회로도 편집기에서 확인

### 파일 형식
- KiCad 8.0 S-expression 형식
- 심볼 라이브러리 포함

---

## 2. OrCAD Capture TCL 스크립트

### 사용 방법
1. OrCAD Capture 17.x 이상 실행
2. 빈 프로젝트 생성
3. Tools → TCL → Execute Script
4. `BL520_Charger.tcl` 선택

### 기능
- 부품 자동 배치
- 넷 연결 정보
- BOM 생성
- 부품 요약 출력

### 출력 예시
```
BL520: ==========================================
BL520: BL520 Charger Board - OrCAD TCL Generator
BL520: ==========================================
...
BL520: Total components: 38
```

---

## 3. KiCad Python API 스크립트

### 사용 방법 (방법 1: KiCad 내부)
1. KiCad 열기
2. Tools → Scripting Console
3. 스크립트 실행:
   ```python
   exec(open('/path/to/BL520_kicad_generator.py').read())
   ```

### 사용 방법 (방법 2: 독립 실행)
```bash
python BL520_kicad_generator.py
```

### 생성되는 파일
- `BL520_Charger_generated.kicad_sch` - 회로도
- `BL520_BOM_generated.md` - BOM (Markdown)
- `BL520_Netlist_generated.txt` - 넷리스트

---

## 부품 요약

| 카테고리 | 수량 | 부품 |
|----------|------|------|
| Connectors | 3 | DC1, J1, CHARGE |
| Diodes | 2 | D1, D2 (SS34) |
| Inductors | 3 | L1, L2 (10µH), L3 (CMC) |
| Capacitors | 6 | C2-C7 |
| ICs | 1 | U1 (AMS1117-5.0) |
| LEDs | 5 | LED1-5 |
| Transistors | 11 | Q1-Q11 |
| Resistors | 7 | R9-R15 |
| **Total** | **38** | |

---

## 핵심 사양

### 트랜지스터 패키지
| 부품 | 패키지 | 용도 |
|------|--------|------|
| Q1, Q3, Q5, Q7, Q9 | **SOT-89** | 고전류 IR LED 드라이버 |
| Q2, Q4, Q6, Q8, Q10, Q11 | **SOT-23-3** | 신호 제어 |

### LED5 사양
- **타입**: Green 2-Color (녹색 2색)
- **패키지**: 5mm 3-pin
- **렌즈**: Milky (우유빛 확산)
- **용도**: 충전 상태 표시

---

## 호환성

| 도구 | 버전 | 상태 |
|------|------|------|
| KiCad | 8.0+ | ✅ 테스트됨 |
| KiCad | 6.0-7.0 | ⚠️ 수정 필요 가능 |
| OrCAD Capture | 17.x+ | ✅ 지원 |
| Python | 3.8+ | ✅ 테스트됨 |

---

## 참고 사항

1. **역설계 기반**: PCB 이미지 분석으로 일부 값이 실제와 다를 수 있음
2. **IC1 미확인**: 컨트롤러 IC 모델 확인 필요
3. **연결 확인 필요**: 실제 PCB와 대조 권장

---

*Generated: 2024*
*Board: BL520 Charger Board V1.0 (2019-03-16-J)*
