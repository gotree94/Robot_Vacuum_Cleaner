#!/usr/bin/env python3
"""
기어드 모터 설계 계산기
========================
DC 모터 사양과 목표 성능을 입력하면 필요한 기어비와 기어 구성을 자동으로 계산합니다.

이론적 배경:
-----------
1. DC 모터 기본 방정식
   - 역기전력(Back-EMF): E = Ke × ω
   - 토크: T = Kt × I
   - 무부하 속도: ω_no_load = V / Ke
   - 정지 토크: T_stall = Kt × I_stall

2. 기어 감속 원리
   - 속도 관계: ω_out = ω_in / G (G: 총 기어비)
   - 토크 관계: T_out = T_in × G × η (η: 효율)
   - 출력 = 입력 - 손실

3. 다단 기어 시스템
   - 총 기어비: G_total = G1 × G2 × G3 × ...
   - 총 효율: η_total = η1 × η2 × η3 × ...

Author: Claude (Anthropic)
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
import json


@dataclass
class DCMotorSpec:
    """DC 모터 사양 데이터 클래스"""
    name: str                    # 모터 이름/모델
    voltage_nominal: float       # 정격 전압 [V]
    current_no_load: float       # 무부하 전류 [A]
    current_stall: float         # 정지(스톨) 전류 [A]
    rpm_no_load: float           # 무부하 회전수 [RPM]
    torque_stall: float          # 정지 토크 [mNm]
    diameter: float              # 모터 직경 [mm]
    length: float                # 모터 길이 [mm]
    weight: float                # 모터 무게 [g]
    
    @property
    def omega_no_load(self) -> float:
        """무부하 각속도 [rad/s]"""
        return self.rpm_no_load * 2 * math.pi / 60
    
    @property
    def torque_stall_Nm(self) -> float:
        """정지 토크 [Nm]"""
        return self.torque_stall / 1000
    
    @property
    def Ke(self) -> float:
        """역기전력 상수 [V/(rad/s)]"""
        return self.voltage_nominal / self.omega_no_load
    
    @property
    def Kt(self) -> float:
        """토크 상수 [Nm/A]"""
        return self.torque_stall_Nm / self.current_stall
    
    @property
    def R_armature(self) -> float:
        """전기자 저항 [Ω] (추정값)"""
        return self.voltage_nominal / self.current_stall
    
    @property
    def power_max(self) -> float:
        """최대 기계적 출력 [W] (정지토크의 25% 지점에서 발생)"""
        return (self.torque_stall_Nm / 4) * (self.omega_no_load / 2)
    
    def get_operating_point(self, load_torque_Nm: float) -> Tuple[float, float, float, float]:
        """
        주어진 부하 토크에서의 동작점 계산
        
        Returns:
            (rpm, current, power_mech, efficiency)
        """
        if load_torque_Nm > self.torque_stall_Nm:
            return (0, self.current_stall, 0, 0)
        
        # 선형 토크-속도 특성 가정
        rpm = self.rpm_no_load * (1 - load_torque_Nm / self.torque_stall_Nm)
        omega = rpm * 2 * math.pi / 60
        
        # 전류 계산
        current = self.current_no_load + (self.current_stall - self.current_no_load) * (load_torque_Nm / self.torque_stall_Nm)
        
        # 기계적 출력
        power_mech = load_torque_Nm * omega
        
        # 전기적 입력
        power_elec = self.voltage_nominal * current
        
        # 효율
        efficiency = power_mech / power_elec if power_elec > 0 else 0
        
        return (rpm, current, power_mech, efficiency)


@dataclass
class GearStage:
    """단일 기어 단 정보"""
    ratio: float                 # 기어비 (>1: 감속)
    efficiency: float            # 효율 (0~1)
    gear_type: str              # 기어 종류
    teeth_driving: int          # 구동 기어 잇수
    teeth_driven: int           # 피동 기어 잇수
    module: float               # 모듈 [mm]
    
    @property
    def pitch_diameter_driving(self) -> float:
        """구동 기어 피치원 직경 [mm]"""
        return self.module * self.teeth_driving
    
    @property
    def pitch_diameter_driven(self) -> float:
        """피동 기어 피치원 직경 [mm]"""
        return self.module * self.teeth_driven


@dataclass
class TargetSpec:
    """목표 사양"""
    rpm_output: float            # 목표 출력 회전수 [RPM]
    torque_output_Nm: float      # 목표 출력 토크 [Nm]
    
    @property
    def torque_output_mNm(self) -> float:
        return self.torque_output_Nm * 1000
    
    @property
    def power_output(self) -> float:
        """목표 출력 [W]"""
        omega = self.rpm_output * 2 * math.pi / 60
        return self.torque_output_Nm * omega


class GearTrainDesigner:
    """기어 트레인 설계 클래스"""
    
    # 기어 종류별 일반적인 효율
    GEAR_EFFICIENCY = {
        'spur': 0.98,           # 평기어
        'helical': 0.97,        # 헬리컬 기어
        'bevel': 0.96,          # 베벨 기어
        'worm': 0.75,           # 웜 기어 (자기 잠금 가능)
        'planetary': 0.97,      # 유성 기어
    }
    
    # 단일 단에서 권장 최대 기어비
    MAX_RATIO_PER_STAGE = {
        'spur': 6.0,
        'helical': 8.0,
        'bevel': 5.0,
        'worm': 60.0,
        'planetary': 10.0,
    }
    
    # 표준 모듈 값 [mm]
    STANDARD_MODULES = [0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
    
    def __init__(self, motor: DCMotorSpec, target: TargetSpec, 
                 gear_type: str = 'spur', motor_efficiency: float = 0.85):
        self.motor = motor
        self.target = target
        self.gear_type = gear_type
        self.motor_efficiency = motor_efficiency
        self.gear_stages: List[GearStage] = []
        
    def calculate_required_ratio(self) -> float:
        """필요한 총 기어비 계산"""
        return self.motor.rpm_no_load / self.target.rpm_output
    
    def calculate_required_motor_torque(self, total_ratio: float, total_efficiency: float) -> float:
        """모터에 필요한 토크 계산 [Nm]"""
        return self.target.torque_output_Nm / (total_ratio * total_efficiency)
    
    def design_gear_train(self, preferred_stages: int = None) -> List[GearStage]:
        """
        기어 트레인 자동 설계
        
        Args:
            preferred_stages: 선호하는 기어 단수 (None이면 자동 결정)
        """
        total_ratio = self.calculate_required_ratio()
        
        if total_ratio < 1:
            print("⚠️ 경고: 기어비 < 1 (증속이 필요함). 모터 선택을 재검토하세요.")
            return []
        
        # 필요한 단수 결정
        max_ratio = self.MAX_RATIO_PER_STAGE[self.gear_type]
        if preferred_stages:
            num_stages = preferred_stages
        else:
            num_stages = max(1, math.ceil(math.log(total_ratio) / math.log(max_ratio)))
        
        # 각 단의 기어비 균등 분배
        ratio_per_stage = total_ratio ** (1 / num_stages)
        
        # 기어비가 너무 크면 단수 증가
        while ratio_per_stage > max_ratio and num_stages < 5:
            num_stages += 1
            ratio_per_stage = total_ratio ** (1 / num_stages)
        
        gear_efficiency = self.GEAR_EFFICIENCY[self.gear_type]
        
        self.gear_stages = []
        for i in range(num_stages):
            # 기어 잇수 결정 (최소 12치)
            teeth_driving = 18  # 구동 기어 기본 잇수
            teeth_driven = round(teeth_driving * ratio_per_stage)
            actual_ratio = teeth_driven / teeth_driving
            
            # 모듈 선택 (크기 고려)
            module = self._select_module(teeth_driving, teeth_driven, i)
            
            stage = GearStage(
                ratio=actual_ratio,
                efficiency=gear_efficiency,
                gear_type=self.gear_type,
                teeth_driving=teeth_driving,
                teeth_driven=teeth_driven,
                module=module
            )
            self.gear_stages.append(stage)
        
        return self.gear_stages
    
    def _select_module(self, z1: int, z2: int, stage_index: int) -> float:
        """적절한 모듈 선택"""
        # 첫 번째 단은 작은 모듈, 이후 단계는 점점 큰 모듈
        # 기본적으로 모터 크기에 따라 결정
        base_module_index = 2 + stage_index  # 0.5mm부터 시작
        if base_module_index >= len(self.STANDARD_MODULES):
            base_module_index = len(self.STANDARD_MODULES) - 1
        return self.STANDARD_MODULES[base_module_index]
    
    def get_total_ratio(self) -> float:
        """총 기어비"""
        if not self.gear_stages:
            return 1.0
        ratio = 1.0
        for stage in self.gear_stages:
            ratio *= stage.ratio
        return ratio
    
    def get_total_efficiency(self) -> float:
        """총 효율"""
        if not self.gear_stages:
            return 1.0
        eff = self.motor_efficiency
        for stage in self.gear_stages:
            eff *= stage.efficiency
        return eff
    
    def analyze_performance(self) -> dict:
        """성능 분석"""
        total_ratio = self.get_total_ratio()
        total_efficiency = self.get_total_efficiency()
        
        # 출력 측 성능
        output_rpm = self.motor.rpm_no_load / total_ratio
        
        # 필요한 모터 토크
        required_motor_torque = self.calculate_required_motor_torque(total_ratio, total_efficiency)
        
        # 모터 동작점 분석
        motor_rpm, motor_current, motor_power, motor_eff = self.motor.get_operating_point(required_motor_torque)
        
        # 실제 출력 계산
        actual_output_rpm = motor_rpm / total_ratio
        actual_output_torque = required_motor_torque * total_ratio * total_efficiency
        actual_output_power = actual_output_torque * (actual_output_rpm * 2 * math.pi / 60)
        
        # 마진 계산
        torque_margin = (self.motor.torque_stall_Nm - required_motor_torque) / self.motor.torque_stall_Nm * 100
        
        return {
            'total_ratio': total_ratio,
            'total_efficiency': total_efficiency,
            'output_rpm_no_load': output_rpm,
            'required_motor_torque_Nm': required_motor_torque,
            'required_motor_torque_mNm': required_motor_torque * 1000,
            'motor_operating_rpm': motor_rpm,
            'motor_operating_current': motor_current,
            'actual_output_rpm': actual_output_rpm,
            'actual_output_torque_Nm': actual_output_torque,
            'actual_output_torque_mNm': actual_output_torque * 1000,
            'actual_output_power_W': actual_output_power,
            'torque_margin_percent': torque_margin,
            'system_efficiency': total_efficiency * motor_eff,
            'feasible': required_motor_torque <= self.motor.torque_stall_Nm * 0.8
        }


def print_motor_info(motor: DCMotorSpec):
    """모터 정보 출력"""
    print("\n" + "="*70)
    print(f"  DC 모터 사양: {motor.name}")
    print("="*70)
    
    print(f"\n  [기본 사양]")
    print(f"    정격 전압        : {motor.voltage_nominal:>8.1f} V")
    print(f"    무부하 전류      : {motor.current_no_load:>8.3f} A")
    print(f"    정지(스톨) 전류  : {motor.current_stall:>8.2f} A")
    print(f"    무부하 회전수    : {motor.rpm_no_load:>8.0f} RPM")
    print(f"    정지 토크        : {motor.torque_stall:>8.1f} mNm")
    
    print(f"\n  [물리적 사양]")
    print(f"    직경             : {motor.diameter:>8.1f} mm")
    print(f"    길이             : {motor.length:>8.1f} mm")
    print(f"    무게             : {motor.weight:>8.1f} g")
    
    print(f"\n  [계산된 상수]")
    print(f"    역기전력 상수 Ke : {motor.Ke*1000:>8.3f} mV/(rad/s)")
    print(f"    토크 상수 Kt     : {motor.Kt*1000:>8.3f} mNm/A")
    print(f"    전기자 저항 Ra   : {motor.R_armature:>8.2f} Ω")
    print(f"    최대 출력        : {motor.power_max:>8.3f} W")


def print_target_info(target: TargetSpec):
    """목표 사양 출력"""
    print("\n" + "="*70)
    print("  목표 사양")
    print("="*70)
    print(f"    목표 출력 회전수 : {target.rpm_output:>8.1f} RPM")
    print(f"    목표 출력 토크   : {target.torque_output_mNm:>8.1f} mNm ({target.torque_output_Nm:.4f} Nm)")
    print(f"    목표 출력        : {target.power_output:>8.3f} W")


def print_gear_design(designer: GearTrainDesigner):
    """기어 설계 결과 출력"""
    print("\n" + "="*70)
    print("  기어 트레인 설계 결과")
    print("="*70)
    
    print(f"\n  기어 종류: {designer.gear_type.upper()}")
    print(f"  기어 단수: {len(designer.gear_stages)}단")
    
    for i, stage in enumerate(designer.gear_stages, 1):
        print(f"\n  [Stage {i}]")
        print(f"    기어비           : {stage.ratio:>8.2f}:1")
        print(f"    구동 기어 잇수   : {stage.teeth_driving:>8d} 치")
        print(f"    피동 기어 잇수   : {stage.teeth_driven:>8d} 치")
        print(f"    모듈             : {stage.module:>8.2f} mm")
        print(f"    구동 기어 PCD    : {stage.pitch_diameter_driving:>8.1f} mm")
        print(f"    피동 기어 PCD    : {stage.pitch_diameter_driven:>8.1f} mm")
        print(f"    단 효율          : {stage.efficiency*100:>8.1f} %")


def print_performance_analysis(perf: dict):
    """성능 분석 결과 출력"""
    print("\n" + "="*70)
    print("  성능 분석 결과")
    print("="*70)
    
    print(f"\n  [기어 시스템]")
    print(f"    총 기어비        : {perf['total_ratio']:>8.2f}:1")
    print(f"    총 기어 효율     : {perf['total_efficiency']*100:>8.1f} %")
    
    print(f"\n  [모터 동작점]")
    print(f"    필요 모터 토크   : {perf['required_motor_torque_mNm']:>8.2f} mNm")
    print(f"    모터 회전수      : {perf['motor_operating_rpm']:>8.0f} RPM")
    print(f"    모터 전류        : {perf['motor_operating_current']:>8.3f} A")
    print(f"    토크 마진        : {perf['torque_margin_percent']:>8.1f} %")
    
    print(f"\n  [출력 성능]")
    print(f"    출력 회전수      : {perf['actual_output_rpm']:>8.1f} RPM")
    print(f"    출력 토크        : {perf['actual_output_torque_mNm']:>8.2f} mNm ({perf['actual_output_torque_Nm']:.4f} Nm)")
    print(f"    출력 파워        : {perf['actual_output_power_W']:>8.3f} W")
    print(f"    시스템 효율      : {perf['system_efficiency']*100:>8.1f} %")
    
    print(f"\n  [설계 적합성]")
    if perf['feasible']:
        print("    ✅ 설계 가능 - 모터가 목표 성능을 달성할 수 있습니다.")
    else:
        print("    ❌ 설계 불가 - 더 강력한 모터가 필요합니다.")
        print("       (토크 마진이 20% 미만입니다)")


def print_theory():
    """이론 설명 출력"""
    print("\n" + "="*70)
    print("  기어드 모터 설계 이론")
    print("="*70)
    
    theory_text = """
  1. DC 모터 기본 특성
  ───────────────────────────────────────────────────────────────────
  
  DC 모터는 전기 에너지를 기계적 회전 에너지로 변환합니다.
  
  • 역기전력 (Back-EMF): E = Ke × ω
    - 모터가 회전하면 역방향 전압이 발생
    - Ke: 역기전력 상수 [V/(rad/s)]
    
  • 토크 생성: T = Kt × I
    - 전류에 비례하여 토크 발생
    - Kt: 토크 상수 [Nm/A]
    - 이상적으로 Ke = Kt (SI 단위계에서)
    
  • 토크-속도 특성 (선형):
    
    토크(T) ▲
            │╲
    T_stall │ ╲
            │  ╲
            │   ╲
            │    ╲
            └─────╲──────► 속도(ω)
                   ω_no_load
    
    ω = ω_no_load × (1 - T/T_stall)
    
  • 최대 효율점: 정지 토크의 약 50% 지점
  • 최대 출력점: 정지 토크의 약 50% 지점


  2. 기어 감속 원리
  ───────────────────────────────────────────────────────────────────
  
  기어비 G = N_driven / N_driving = 피동기어 잇수 / 구동기어 잇수
  
  • 속도 변환: ω_out = ω_in / G
    - G > 1: 감속 (속도 감소)
    - G < 1: 증속 (속도 증가)
    
  • 토크 변환: T_out = T_in × G × η
    - η: 기어 효율 (0 < η < 1)
    - 감속 시 토크 증가 (힘 증폭)
    
  • 출력 보존 (이상적):
    P_out = P_in × η
    T_out × ω_out = (T_in × ω_in) × η


  3. 다단 기어 시스템
  ───────────────────────────────────────────────────────────────────
  
  큰 기어비가 필요한 경우 여러 단을 직렬 연결합니다.
  
    ┌─────┐    ┌─────┐    ┌─────┐
    │ G1  │────│ G2  │────│ G3  │
    └─────┘    └─────┘    └─────┘
      η1         η2         η3
  
  • 총 기어비: G_total = G1 × G2 × G3
  • 총 효율: η_total = η1 × η2 × η3
  
  예) 100:1 감속 필요 시
      - 단일 단: 100:1 (비실용적, 기어가 너무 큼)
      - 3단: 약 4.64:1 × 4.64:1 × 4.64:1 ≈ 100:1


  4. 기어 종류별 특성
  ───────────────────────────────────────────────────────────────────
  
  │ 기어 종류   │ 효율  │ 최대 기어비 │ 특징                    │
  │────────────│──────│───────────│────────────────────────│
  │ 평기어     │ ~98% │ 6:1       │ 단순, 저렴, 소음 있음    │
  │ 헬리컬     │ ~97% │ 8:1       │ 저소음, 축방향 하중      │
  │ 베벨      │ ~96% │ 5:1       │ 축 방향 변경 가능        │
  │ 웜        │ ~75% │ 60:1      │ 자기잠금, 큰 감속비      │
  │ 유성기어   │ ~97% │ 10:1      │ 컴팩트, 동축, 고토크     │


  5. 기어 치수 설계
  ───────────────────────────────────────────────────────────────────
  
  • 모듈 (m): 기어 크기의 기준
    - 피치원 직경: d = m × z (z: 잇수)
    - 이끝원 직경: da = d + 2m
    - 이뿌리원 직경: df = d - 2.5m
    
  • 중심거리: a = m × (z1 + z2) / 2
  
  • 최소 잇수: 일반적으로 12~18치 (언더컷 방지)


  6. 설계 시 고려사항
  ───────────────────────────────────────────────────────────────────
  
  • 토크 마진: 정지 토크의 80% 이하에서 운전 권장
  • 열 관리: 연속 운전 시 모터 발열 고려
  • 백래시: 정밀 위치 제어 시 중요
  • 관성: 부하 관성과 모터 관성의 매칭
  • 공진: 시스템 고유진동수 회피
"""
    print(theory_text)


def interactive_mode():
    """대화형 모드로 실행"""
    print("\n" + "="*70)
    print("  기어드 모터 설계 계산기")
    print("="*70)
    print("\n  DC 모터의 사양과 목표 성능을 입력하면")
    print("  필요한 기어비와 기어 구성을 자동으로 계산합니다.\n")
    
    # 모터 사양 입력
    print("  [DC 모터 사양 입력]")
    print("  (Enter를 누르면 기본값 사용)\n")
    
    def get_float(prompt, default):
        val = input(f"    {prompt} [{default}]: ").strip()
        return float(val) if val else default
    
    def get_str(prompt, default):
        val = input(f"    {prompt} [{default}]: ").strip()
        return val if val else default
    
    name = get_str("모터 이름", "FA-130")
    voltage = get_float("정격 전압 (V)", 3.0)
    current_no_load = get_float("무부하 전류 (A)", 0.15)
    current_stall = get_float("정지(스톨) 전류 (A)", 2.2)
    rpm_no_load = get_float("무부하 회전수 (RPM)", 9600)
    torque_stall = get_float("정지 토크 (mNm)", 11.8)
    diameter = get_float("모터 직경 (mm)", 20.4)
    length = get_float("모터 길이 (mm)", 25.1)
    weight = get_float("모터 무게 (g)", 18.0)
    
    motor = DCMotorSpec(
        name=name,
        voltage_nominal=voltage,
        current_no_load=current_no_load,
        current_stall=current_stall,
        rpm_no_load=rpm_no_load,
        torque_stall=torque_stall,
        diameter=diameter,
        length=length,
        weight=weight
    )
    
    # 목표 사양 입력
    print("\n  [목표 사양 입력]\n")
    target_rpm = get_float("목표 출력 회전수 (RPM)", 100)
    target_torque = get_float("목표 출력 토크 (mNm)", 500)
    
    target = TargetSpec(
        rpm_output=target_rpm,
        torque_output_Nm=target_torque / 1000
    )
    
    # 기어 종류 선택
    print("\n  [기어 종류 선택]")
    print("    1. spur (평기어) - 기본")
    print("    2. helical (헬리컬 기어)")
    print("    3. planetary (유성 기어)")
    print("    4. worm (웜 기어)")
    
    gear_choice = input("\n    선택 [1]: ").strip()
    gear_types = {'1': 'spur', '2': 'helical', '3': 'planetary', '4': 'worm', '': 'spur'}
    gear_type = gear_types.get(gear_choice, 'spur')
    
    # 설계 및 분석
    designer = GearTrainDesigner(motor, target, gear_type)
    designer.design_gear_train()
    performance = designer.analyze_performance()
    
    # 결과 출력
    print_motor_info(motor)
    print_target_info(target)
    print_gear_design(designer)
    print_performance_analysis(performance)
    
    # 이론 출력 여부
    show_theory = input("\n  이론 설명을 보시겠습니까? (y/n) [n]: ").strip().lower()
    if show_theory == 'y':
        print_theory()
    
    return motor, target, designer, performance


def example_calculation():
    """예제 계산 실행"""
    print("\n" + "="*70)
    print("  기어드 모터 설계 예제")
    print("="*70)
    
    # 예제 1: 소형 로봇용 모터 (FA-130 기반)
    motor1 = DCMotorSpec(
        name="FA-130 (3V)",
        voltage_nominal=3.0,
        current_no_load=0.15,
        current_stall=2.2,
        rpm_no_load=9600,
        torque_stall=11.8,
        diameter=20.4,
        length=25.1,
        weight=18.0
    )
    
    # 예제 2: 중형 모터 (RS-385)
    motor2 = DCMotorSpec(
        name="RS-385 (12V)",
        voltage_nominal=12.0,
        current_no_load=0.08,
        current_stall=3.8,
        rpm_no_load=7400,
        torque_stall=98.0,
        diameter=28.0,
        length=38.0,
        weight=65.0
    )
    
    # 목표 사양: 로봇 바퀴 구동 (100 RPM, 500 mNm)
    target = TargetSpec(
        rpm_output=100,
        torque_output_Nm=0.5
    )
    
    print("\n  예제: 로봇 바퀴 구동 시스템 설계")
    print("  목표: 100 RPM, 500 mNm 토크")
    
    for motor in [motor1, motor2]:
        print_motor_info(motor)
        print_target_info(target)
        
        designer = GearTrainDesigner(motor, target, 'spur')
        designer.design_gear_train()
        performance = designer.analyze_performance()
        
        print_gear_design(designer)
        print_performance_analysis(performance)
    
    print_theory()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        example_calculation()
    else:
        interactive_mode()
