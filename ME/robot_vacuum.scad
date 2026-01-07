// ============================================
// 로봇 청소기 3D 모델 (Mid-range)
// Robot Vacuum Cleaner 3D Model
// 사양: Ø350 × H98mm, LiDAR + 물걸레
// ============================================

// === 파라미터 설정 ===
// 메인 치수 (mm)
body_diameter = 350;
body_height = 75;
total_height = 98;

// LiDAR 터렛
lidar_diameter = 70;
lidar_height = 23;
lidar_offset_y = 30;  // 중심에서 앞쪽으로 오프셋

// 범퍼
bumper_width = 10;
bumper_height = 50;
bumper_angle = 200;  // 전면 범퍼 각도

// 휠
wheel_diameter = 70;
wheel_width = 25;
wheel_offset_x = 100;  // 중심에서 좌우 거리
wheel_offset_y = 20;   // 중심에서 뒤쪽으로

// 캐스터 휠
caster_diameter = 30;
caster_offset_y = 130; // 전방

// 브러시
main_brush_length = 180;
main_brush_diameter = 45;
side_brush_diameter = 100;
side_brush_offset = 120;

// 버튼
button_diameter = 45;
button_height = 3;

// 충전 접점
contact_width = 8;
contact_height = 15;
contact_offset = 60;

// 물걸레 모듈
mop_diameter = 120;
mop_height = 8;
mop_offset_y = -80;

// 해상도
$fn = 80;

// === 색상 정의 ===
color_body_top = [0.95, 0.95, 0.95];      // 흰색 상판
color_body_bottom = [0.2, 0.2, 0.2];      // 다크 그레이 하판
color_bumper = [0.3, 0.3, 0.3];           // 그레이 범퍼
color_lidar = [0.15, 0.15, 0.15];         // 블랙 LiDAR
color_lidar_window = [0.1, 0.1, 0.1, 0.5]; // 반투명
color_wheel = [0.1, 0.1, 0.1];            // 블랙 휠
color_brush = [0.8, 0.2, 0.2];            // 빨간 브러시
color_button = [0.9, 0.9, 0.9];           // 버튼
color_led = [0.2, 0.5, 1.0];              // LED 파란색
color_contact = [0.8, 0.7, 0.2];          // 금색 접점
color_mop = [0.6, 0.8, 1.0];              // 물걸레 패드

// === 메인 모듈 ===

// 전체 로봇 청소기 조립
module robot_vacuum() {
    // 하판 (베이스)
    color(color_body_bottom)
    bottom_plate();
    
    // 상판 (커버)
    color(color_body_top)
    top_cover();
    
    // 범퍼
    color(color_bumper)
    bumper();
    
    // LiDAR 터렛
    translate([0, lidar_offset_y, body_height])
    lidar_turret();
    
    // 버튼
    translate([0, 50, body_height])
    button_assembly();
    
    // LED 표시등
    translate([0, 80, body_height - 2])
    led_indicator();
    
    // 구동 휠 (좌)
    translate([-wheel_offset_x, -wheel_offset_y, 15])
    rotate([0, 90, 0])
    color(color_wheel)
    drive_wheel();
    
    // 구동 휠 (우)
    translate([wheel_offset_x, -wheel_offset_y, 15])
    rotate([0, -90, 0])
    color(color_wheel)
    drive_wheel();
    
    // 캐스터 휠
    translate([0, caster_offset_y, 8])
    color(color_wheel)
    caster_wheel();
    
    // 메인 브러시
    translate([0, 50, 10])
    rotate([0, 90, 0])
    color(color_brush)
    main_brush();
    
    // 사이드 브러시 (좌)
    translate([-side_brush_offset, 100, 5])
    color(color_brush)
    side_brush();
    
    // 사이드 브러시 (우)
    translate([side_brush_offset, 100, 5])
    color(color_brush)
    side_brush();
    
    // 충전 접점
    translate([0, -body_diameter/2 + 5, 20])
    charging_contacts();
    
    // 물걸레 모듈
    translate([0, mop_offset_y, 3])
    mop_module();
    
    // 절벽 센서
    cliff_sensors();
    
    // 먼지통 도어 (상단)
    translate([0, -60, body_height])
    dustbin_door();
}

// 하판 모듈
module bottom_plate() {
    difference() {
        // 메인 바디
        cylinder(h = body_height * 0.4, d = body_diameter);
        
        // 휠 공간 (좌)
        translate([-wheel_offset_x, -wheel_offset_y, -1])
        cube([wheel_width + 10, wheel_diameter + 20, body_height * 0.4 + 2], center = true);
        
        // 휠 공간 (우)
        translate([wheel_offset_x, -wheel_offset_y, -1])
        cube([wheel_width + 10, wheel_diameter + 20, body_height * 0.4 + 2], center = true);
        
        // 브러시 공간
        translate([0, 50, -1])
        cube([main_brush_length + 20, 60, 20], center = true);
        
        // 물걸레 공간
        translate([0, mop_offset_y, -1])
        cylinder(h = 15, d = mop_diameter * 2.2);
    }
}

// 상판 모듈
module top_cover() {
    translate([0, 0, body_height * 0.4])
    difference() {
        union() {
            // 메인 커버 (약간 둥근 형태)
            scale([1, 1, 0.8])
            difference() {
                sphere(d = body_diameter);
                translate([0, 0, -body_diameter/2])
                cube([body_diameter + 10, body_diameter + 10, body_diameter], center = true);
                translate([0, 0, body_diameter * 0.25])
                cube([body_diameter + 10, body_diameter + 10, body_diameter], center = true);
            }
        }
        
        // LiDAR 구멍
        translate([0, lidar_offset_y, 0])
        cylinder(h = 100, d = lidar_diameter + 2);
        
        // 버튼 구멍
        translate([0, 50, body_height * 0.5])
        cylinder(h = 20, d = button_diameter + 2);
        
        // 먼지통 도어 컷아웃
        translate([0, -60, body_height * 0.4])
        cube([100, 80, 30], center = true);
    }
}

// 범퍼 모듈
module bumper() {
    difference() {
        // 외부 범퍼
        cylinder(h = bumper_height, d = body_diameter + bumper_width * 2);
        
        // 내부 컷
        translate([0, 0, -1])
        cylinder(h = bumper_height + 2, d = body_diameter);
        
        // 후면 컷 (충전 접점 부분)
        translate([0, -body_diameter/2, -1])
        cube([body_diameter, body_diameter/2, bumper_height + 2], center = true);
        
        // 상단 경사
        translate([0, 0, bumper_height - 10])
        difference() {
            cylinder(h = 20, d = body_diameter + bumper_width * 4);
            cylinder(h = 20, d1 = body_diameter + bumper_width * 2, d2 = body_diameter - 10);
        }
    }
    
    // 범퍼 고무 라인
    translate([0, 0, bumper_height/2])
    difference() {
        cylinder(h = 5, d = body_diameter + bumper_width * 2 + 2);
        cylinder(h = 6, d = body_diameter + bumper_width * 2 - 2);
        translate([0, -body_diameter/2, 0])
        cube([body_diameter, body_diameter/2, 10], center = true);
    }
}

// LiDAR 터렛 모듈
module lidar_turret() {
    // 베이스
    color(color_lidar)
    cylinder(h = 5, d = lidar_diameter + 10);
    
    // 회전부
    translate([0, 0, 5])
    color(color_lidar)
    cylinder(h = lidar_height - 8, d = lidar_diameter);
    
    // 투명 윈도우
    translate([0, 0, 5])
    color(color_lidar_window)
    difference() {
        cylinder(h = lidar_height - 5, d = lidar_diameter + 2);
        cylinder(h = lidar_height - 4, d = lidar_diameter - 4);
    }
    
    // 상단 캡
    translate([0, 0, lidar_height])
    color(color_lidar)
    cylinder(h = 3, d1 = lidar_diameter, d2 = lidar_diameter - 10);
}

// 버튼 어셈블리
module button_assembly() {
    // 메인 전원 버튼
    color(color_button)
    cylinder(h = button_height, d = button_diameter);
    
    // 버튼 아이콘 (전원 심볼)
    translate([0, 0, button_height])
    color(color_led)
    difference() {
        cylinder(h = 1, d = 20);
        cylinder(h = 2, d = 14);
        translate([0, 5, 0])
        cube([4, 10, 3], center = true);
    }
    
    // 홈 버튼
    translate([35, 0, 0])
    color(color_button)
    cylinder(h = 2, d = 15);
    
    // 스팟 청소 버튼
    translate([-35, 0, 0])
    color(color_button)
    cylinder(h = 2, d = 15);
}

// LED 표시등
module led_indicator() {
    color(color_led)
    hull() {
        translate([-20, 0, 0]) cylinder(h = 2, d = 8);
        translate([20, 0, 0]) cylinder(h = 2, d = 8);
    }
}

// 구동 휠
module drive_wheel() {
    // 타이어
    difference() {
        cylinder(h = wheel_width, d = wheel_diameter);
        translate([0, 0, -1])
        cylinder(h = wheel_width + 2, d = wheel_diameter - 15);
    }
    
    // 휠 허브
    cylinder(h = wheel_width, d = 30);
    
    // 트레드 패턴
    for (i = [0:30:360]) {
        rotate([0, 0, i])
        translate([wheel_diameter/2 - 3, 0, wheel_width/2])
        cube([6, 3, wheel_width - 4], center = true);
    }
}

// 캐스터 휠
module caster_wheel() {
    // 휠
    sphere(d = caster_diameter);
    
    // 하우징
    translate([0, 0, caster_diameter/2])
    cylinder(h = 15, d = caster_diameter + 10);
}

// 메인 브러시
module main_brush() {
    // 브러시 롤러
    cylinder(h = main_brush_length, d = main_brush_diameter);
    
    // 브러시 모
    for (i = [0:20:360]) {
        rotate([0, 0, i])
        translate([main_brush_diameter/2, 0, 0])
        cube([8, 2, main_brush_length], center = true);
    }
    
    // 축
    cylinder(h = main_brush_length + 20, d = 8, center = true);
}

// 사이드 브러시
module side_brush() {
    // 중심 허브
    cylinder(h = 8, d = 20);
    
    // 브러시 암 (3개)
    for (i = [0:120:360]) {
        rotate([0, 0, i])
        translate([side_brush_diameter/2 - 10, 0, 4])
        rotate([0, 0, 15])
        hull() {
            cylinder(h = 3, d = 10);
            translate([40, 10, 0])
            cylinder(h = 2, d = 5);
        }
    }
}

// 충전 접점
module charging_contacts() {
    // 접점 (+)
    translate([-contact_offset/2, 0, 0])
    color(color_contact)
    cube([contact_width, 5, contact_height], center = true);
    
    // 접점 (-)
    translate([contact_offset/2, 0, 0])
    color(color_contact)
    cube([contact_width, 5, contact_height], center = true);
}

// 물걸레 모듈
module mop_module() {
    // 물걸레 디스크 (좌)
    translate([-mop_diameter/2 - 10, 0, 0])
    color(color_mop)
    cylinder(h = mop_height, d = mop_diameter);
    
    // 물걸레 디스크 (우)
    translate([mop_diameter/2 + 10, 0, 0])
    color(color_mop)
    cylinder(h = mop_height, d = mop_diameter);
    
    // 마운트 프레임
    color(color_body_bottom)
    translate([0, 0, mop_height])
    cube([mop_diameter * 2 + 40, 60, 5], center = true);
}

// 절벽 센서
module cliff_sensors() {
    sensor_positions = [
        [100, 100],   // 전방 좌
        [-100, 100],  // 전방 우
        [130, 0],     // 측면 좌
        [-130, 0],    // 측면 우
    ];
    
    for (pos = sensor_positions) {
        translate([pos[0], pos[1], 2])
        color([0.3, 0.3, 0.3])
        cylinder(h = 3, d = 10);
    }
}

// 먼지통 도어
module dustbin_door() {
    color([0.9, 0.9, 0.9])
    difference() {
        cube([95, 75, 8], center = true);
        translate([0, 0, 3])
        cube([85, 65, 6], center = true);
    }
    
    // 손잡이
    translate([0, 30, 4])
    color([0.7, 0.7, 0.7])
    cube([40, 10, 5], center = true);
}

// === 충전 스테이션 ===
module charging_station() {
    // 베이스
    color([0.2, 0.2, 0.2])
    translate([0, -250, 0])
    difference() {
        cube([150, 100, 20], center = true);
        translate([0, 30, 5])
        cube([130, 60, 15], center = true);
    }
    
    // 후면 타워
    color([0.25, 0.25, 0.25])
    translate([0, -290, 40])
    cube([140, 30, 80], center = true);
    
    // 충전 접점
    translate([0, -250, 15])
    color(color_contact)
    union() {
        translate([-contact_offset/2, 40, 0])
        cube([contact_width, 5, 20], center = true);
        translate([contact_offset/2, 40, 0])
        cube([contact_width, 5, 20], center = true);
    }
    
    // IR 송신부
    translate([0, -275, 60])
    color([0.1, 0.1, 0.1])
    cylinder(h = 5, d = 15);
    
    // LED 표시등
    translate([0, -275, 75])
    color([0.2, 0.8, 0.2])
    sphere(d = 8);
}

// === 렌더링 ===

// 로봇 청소기 렌더링
robot_vacuum();

// 충전 스테이션 (선택적)
// charging_station();

// === 내보내기용 개별 모듈 ===
// 아래 주석을 해제하여 개별 부품 내보내기 가능

// translate([400, 0, 0]) bottom_plate();
// translate([400, 400, 0]) top_cover();
// translate([0, 400, 0]) bumper();
// translate([-400, 0, 0]) lidar_turret();
// translate([-400, 400, 0]) drive_wheel();
