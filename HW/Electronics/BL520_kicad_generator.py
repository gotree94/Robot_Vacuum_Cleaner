#!/usr/bin/env python3
"""
BL520 Charger Board V1.0 - KiCad Python Script
Robot Vacuum Charging Station

This script generates a KiCad schematic using the KiCad Python API (pcbnew/eeschema).

Usage:
    Method 1: Run in KiCad Scripting Console
        - Open KiCad -> Tools -> Scripting Console
        - Execute: exec(open('/path/to/BL520_kicad_generator.py').read())
    
    Method 2: Run standalone (generates .kicad_sch file directly)
        - python BL520_kicad_generator.py

Requirements:
    - KiCad 6.0+ with Python scripting support
    - Or standalone execution for file generation

Author: Reverse Engineered
Date: 2024
Rev: 1.2
"""

import os
import sys
import uuid
from datetime import datetime

#==============================================================================
# Component Definitions
#==============================================================================

class Component:
    """Represents a schematic component"""
    def __init__(self, ref, value, footprint, lib_id, x, y, rotation=0):
        self.ref = ref
        self.value = value
        self.footprint = footprint
        self.lib_id = lib_id
        self.x = x
        self.y = y
        self.rotation = rotation
        self.uuid = str(uuid.uuid4())

# Define all components for BL520 Charger Board
COMPONENTS = [
    # DC Input Section
    Component("DC1", "DC_JACK", "Connector_BarrelJack:BarrelJack", "Connector:Barrel_Jack", 25.4, 50.8),
    Component("D1", "SS34", "Diode_SMD:D_SMA", "Device:D_Schottky", 50.8, 48.26),
    Component("D2", "SS34", "Diode_SMD:D_SMA", "Device:D_Schottky", 50.8, 53.34),
    Component("L1", "10uH", "Inductor_SMD:L_1206_3216Metric", "Device:L", 68.58, 48.26, 90),
    Component("L2", "10uH", "Inductor_SMD:L_1206_3216Metric", "Device:L", 68.58, 53.34, 90),
    Component("L3", "CMC", "Inductor_THT:L_Toroid_Horizontal", "Device:L", 25.4, 68.58),
    Component("R9", "10K", "Resistor_SMD:R_1206_3216Metric", "Device:R", 38.1, 68.58),
    Component("R10", "10K", "Resistor_SMD:R_1206_3216Metric", "Device:R", 45.72, 68.58),
    
    # Filter Capacitors
    Component("C2", "100uF/35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", "Device:CP", 86.36, 55.88),
    Component("C3", "10uF/35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", "Device:CP", 93.98, 55.88),
    Component("C5", "100uF/35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", "Device:CP", 101.6, 55.88),
    
    # 5V Regulator Section
    Component("U1", "AMS1117-5.0", "Package_TO_SOT_SMD:SOT-223-3_TabPin2", "Regulator_Linear:AMS1117-5.0", 121.92, 50.8),
    Component("C4", "10uF/16V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", "Device:CP", 109.22, 55.88),
    Component("C6", "10uF/16V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", "Device:CP", 134.62, 55.88),
    Component("C7", "100nF", "Capacitor_SMD:C_0805_2012Metric", "Device:C", 142.24, 55.88),
    
    # IR Transceiver Section
    Component("LED1", "IR_RX", "LED_THT:LED_D5.0mm", "Device:LED", 50.8, 88.9, 270),
    Component("LED2", "IR_TX_940nm", "LED_THT:LED_D5.0mm", "Device:LED", 63.5, 88.9, 270),
    Component("LED3", "IR_RX", "LED_THT:LED_D5.0mm", "Device:LED", 76.2, 88.9, 270),
    Component("LED4", "IR_TX_940nm", "LED_THT:LED_D5.0mm", "Device:LED", 88.9, 88.9, 270),
    Component("LED5", "GREEN_2C_MILKY", "LED_THT:LED_D5.0mm-3", "Device:LED_Dual_AACC", 104.14, 88.9),
    
    # Transistors - SOT-89 (High Current for IR LED)
    Component("Q1", "NPN_SOT89", "Package_TO_SOT_SMD:SOT-89-3", "Transistor_BJT:BCX56", 50.8, 109.22),
    Component("Q3", "NPN_SOT89", "Package_TO_SOT_SMD:SOT-89-3", "Transistor_BJT:BCX56", 63.5, 109.22),
    Component("Q5", "NPN_SOT89", "Package_TO_SOT_SMD:SOT-89-3", "Transistor_BJT:BCX56", 76.2, 109.22),
    Component("Q7", "NPN_SOT89", "Package_TO_SOT_SMD:SOT-89-3", "Transistor_BJT:BCX56", 88.9, 109.22),
    Component("Q9", "NPN_SOT89", "Package_TO_SOT_SMD:SOT-89-3", "Transistor_BJT:BCX56", 101.6, 109.22),
    
    # Transistors - SOT-23-3 (Signal Control)
    Component("Q2", "NPN_SOT23", "Package_TO_SOT_SMD:SOT-23", "Transistor_BJT:BC817", 50.8, 127),
    Component("Q4", "NPN_SOT23", "Package_TO_SOT_SMD:SOT-23", "Transistor_BJT:BC817", 63.5, 127),
    Component("Q6", "NPN_SOT23", "Package_TO_SOT_SMD:SOT-23", "Transistor_BJT:BC817", 76.2, 127),
    Component("Q8", "NPN_SOT23", "Package_TO_SOT_SMD:SOT-23", "Transistor_BJT:BC817", 88.9, 127),
    Component("Q10", "NPN_SOT23", "Package_TO_SOT_SMD:SOT-23", "Transistor_BJT:BC817", 101.6, 127),
    Component("Q11", "NPN_SOT23", "Package_TO_SOT_SMD:SOT-23", "Transistor_BJT:BC817", 114.3, 127),
    
    # Base Resistors
    Component("R11", "1K", "Resistor_SMD:R_0603_1608Metric", "Device:R", 50.8, 119.38, 90),
    Component("R12", "1K", "Resistor_SMD:R_0603_1608Metric", "Device:R", 63.5, 119.38, 90),
    Component("R13", "1K", "Resistor_SMD:R_0603_1608Metric", "Device:R", 76.2, 119.38, 90),
    Component("R14", "1K", "Resistor_SMD:R_0603_1608Metric", "Device:R", 88.9, 119.38, 90),
    Component("R15", "1K", "Resistor_SMD:R_0603_1608Metric", "Device:R", 101.6, 119.38, 90),
    
    # Output Connectors
    Component("J1", "FPC_3PIN", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "Connector:Conn_01x03_Pin", 152.4, 50.8),
    Component("CHARGE", "2PIN", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "Connector:Conn_01x02_Pin", 165.1, 50.8),
]

# Net definitions
NETS = {
    "VIN": ["DC1.1", "D1.1"],
    "GND": ["DC1.2", "D2.1", "C2.2", "C3.2", "C5.2", "C4.2", "C6.2", "C7.2", "U1.GND", 
            "Q1.E", "Q2.E", "Q3.E", "Q4.E", "Q5.E", "Q6.E", "Q7.E", "Q8.E", "Q9.E", "Q10.E", "Q11.E",
            "J1.2", "CHARGE.2"],
    "VIN_FILT": ["D1.2", "D2.2", "L1.1", "L2.1"],
    "VIN_FILT2": ["L1.2", "L2.2", "C2.1", "C3.1", "C5.1", "C4.1", "U1.VI"],
    "+5V": ["U1.VO", "C6.1", "C7.1", "LED1.A", "LED2.A", "LED3.A", "LED4.A", "LED5.COM", "J1.1"],
    "IR_TX1_OUT": ["LED2.K", "Q1.C"],
    "IR_TX2_OUT": ["LED4.K", "Q3.C"],
    "Q1_BASE": ["R11.2", "Q1.B"],
    "Q3_BASE": ["R12.2", "Q3.B"],
    "Q5_BASE": ["R13.2", "Q5.B"],
    "Q7_BASE": ["R14.2", "Q7.B"],
    "Q9_BASE": ["R15.2", "Q9.B"],
    "V_CHARGE": ["CHARGE.1"],
    "FPC_SIG": ["J1.3"],
}

#==============================================================================
# KiCad Schematic Generator
#==============================================================================

class KiCadSchematicGenerator:
    """Generates KiCad schematic files"""
    
    def __init__(self, project_name):
        self.project_name = project_name
        self.uuid = str(uuid.uuid4())
        self.components = []
        self.wires = []
        self.labels = []
        
    def add_component(self, comp):
        """Add a component to the schematic"""
        self.components.append(comp)
        
    def generate_header(self):
        """Generate schematic file header"""
        return f'''(kicad_sch
\t(version 20231120)
\t(generator "BL520_kicad_generator.py")
\t(generator_version "1.0")
\t(uuid "{self.uuid}")
\t(paper "A3")
\t(title_block
\t\t(title "BL520 Charger Board V1.0")
\t\t(date "{datetime.now().strftime('%Y-%m-%d')}")
\t\t(rev "1.2")
\t\t(company "Robot Vacuum Charging Station")
\t\t(comment 1 "Reverse Engineered Schematic")
\t\t(comment 2 "TR: SOT-89 (High Current) / SOT-23-3 (Signal)")
\t\t(comment 3 "LED5: Green 2-Color Milky")
\t)
'''

    def generate_symbol_instance(self, comp, idx):
        """Generate a symbol instance"""
        return f'''
\t(symbol
\t\t(lib_id "{comp.lib_id}")
\t\t(at {comp.x} {comp.y} {comp.rotation})
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{comp.uuid}")
\t\t(property "Reference" "{comp.ref}" (at {comp.x} {comp.y - 5.08} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "{comp.value}" (at {comp.x} {comp.y + 5.08} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "{comp.footprint}" (at {comp.x} {comp.y} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "" (at {comp.x} {comp.y} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(instances
\t\t\t(project "{self.project_name}"
\t\t\t\t(path "/{self.uuid}" (reference "{comp.ref}") (unit 1))
\t\t\t)
\t\t)
\t)
'''

    def generate_text_note(self, text, x, y, size=2.54):
        """Generate a text note"""
        return f'''
\t(text "{text}"
\t\t(exclude_from_sim no)
\t\t(at {x} {y} 0)
\t\t(effects (font (size {size} {size})) (justify left))
\t)
'''

    def generate_schematic(self):
        """Generate complete schematic file content"""
        content = self.generate_header()
        
        # Add title text
        content += self.generate_text_note(
            "BL520 Charger Board V1.0\\n"
            "Robot Vacuum Charging Station\\n"
            "Reverse Engineered\\n\\n"
            "Transistors:\\n"
            "- Q1,3,5,7,9: SOT-89 (High Current)\\n"
            "- Q2,4,6,8,10,11: SOT-23-3 (Signal)\\n\\n"
            "LED5: Green 2-Color, Milky Lens",
            25.4, 20.32, 1.524
        )
        
        # Add section labels
        content += self.generate_text_note("===== DC INPUT =====", 25.4, 40.64, 1.524)
        content += self.generate_text_note("===== 5V REGULATOR =====", 106.68, 40.64, 1.524)
        content += self.generate_text_note("===== IR TRANSCEIVER =====", 50.8, 78.74, 1.524)
        content += self.generate_text_note("===== SOT-89 DRIVERS =====", 50.8, 101.6, 1.524)
        content += self.generate_text_note("===== SOT-23 SIGNAL =====", 50.8, 121.92, 1.524)
        content += self.generate_text_note("===== CONNECTORS =====", 147.32, 40.64, 1.524)
        
        # Add all components
        for idx, comp in enumerate(self.components):
            content += self.generate_symbol_instance(comp, idx)
        
        # Close the schematic
        content += "\n)\n"
        
        return content

    def save(self, filepath):
        """Save schematic to file"""
        content = self.generate_schematic()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Schematic saved to: {filepath}")

#==============================================================================
# BOM Generator
#==============================================================================

def generate_bom(components, filepath):
    """Generate Bill of Materials"""
    
    bom_content = """# BL520 Charger Board V1.0 - Bill of Materials
# Generated by KiCad Python Script
# Date: {date}

| Item | Reference | Value | Footprint | Package |
|------|-----------|-------|-----------|---------|
""".format(date=datetime.now().strftime('%Y-%m-%d'))
    
    for idx, comp in enumerate(components, 1):
        pkg = comp.footprint.split(':')[-1] if ':' in comp.footprint else comp.footprint
        bom_content += f"| {idx} | {comp.ref} | {comp.value} | {comp.footprint} | {pkg} |\n"
    
    bom_content += f"\n**Total Components: {len(components)}**\n"
    
    # Summary by type
    bom_content += """
## Summary by Type

| Category | Count | Notes |
|----------|-------|-------|
| Connectors | 3 | DC1, J1, CHARGE |
| Diodes | 2 | D1, D2 (SS34) |
| Inductors | 3 | L1, L2, L3 |
| Capacitors | 6 | C2-C7 |
| ICs | 1 | U1 (AMS1117-5.0) |
| LEDs | 5 | LED1-5 |
| Transistors (SOT-89) | 5 | Q1,3,5,7,9 - High Current |
| Transistors (SOT-23) | 6 | Q2,4,6,8,10,11 - Signal |
| Resistors | 7 | R9-R15 |

## Special Notes

- **LED5**: Green 2-Color LED with milky diffused lens (5mm, 3-pin)
- **Q1,Q3,Q5,Q7,Q9**: SOT-89 package for high current IR LED driving (~500mA)
- **Q2,Q4,Q6,Q8,Q10,Q11**: SOT-23-3 package for signal control
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(bom_content)
    print(f"BOM saved to: {filepath}")

#==============================================================================
# Netlist Generator
#==============================================================================

def generate_netlist(components, nets, filepath):
    """Generate netlist file"""
    
    netlist_content = """# BL520 Charger Board V1.0 - Netlist
# Generated by KiCad Python Script
# Date: {date}

""".format(date=datetime.now().strftime('%Y-%m-%d'))
    
    netlist_content += "# COMPONENTS\n"
    netlist_content += "-" * 60 + "\n"
    for comp in components:
        netlist_content += f"{comp.ref:10} {comp.value:20} {comp.footprint}\n"
    
    netlist_content += "\n# NETS\n"
    netlist_content += "-" * 60 + "\n"
    for net_name, pins in nets.items():
        netlist_content += f"\n{net_name}:\n"
        for pin in pins:
            netlist_content += f"    {pin}\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(netlist_content)
    print(f"Netlist saved to: {filepath}")

#==============================================================================
# Main Execution
#==============================================================================

def main():
    """Main function"""
    
    print("=" * 60)
    print("BL520 Charger Board V1.0 - KiCad Python Generator")
    print("=" * 60)
    print()
    
    # Output directory
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create schematic generator
    generator = KiCadSchematicGenerator("BL520_Charger")
    
    # Add all components
    for comp in COMPONENTS:
        generator.add_component(comp)
    
    print(f"Total components: {len(COMPONENTS)}")
    print()
    
    # Component summary
    print("Component Summary:")
    print("-" * 40)
    
    categories = {
        'Connectors': ['DC', 'J', 'CHARGE'],
        'Diodes': ['D'],
        'Inductors': ['L'],
        'Capacitors': ['C'],
        'ICs': ['U'],
        'LEDs': ['LED'],
        'Transistors': ['Q'],
        'Resistors': ['R'],
    }
    
    for cat, prefixes in categories.items():
        count = sum(1 for c in COMPONENTS if any(c.ref.startswith(p) for p in prefixes))
        if cat == 'Diodes':
            count = sum(1 for c in COMPONENTS if c.ref.startswith('D') and not c.ref.startswith('DC'))
        print(f"  {cat:15}: {count}")
    
    print()
    print("Transistor Packages:")
    print("  SOT-89 (Q1,3,5,7,9):     High current IR LED drivers")
    print("  SOT-23-3 (Q2,4,6,8,10,11): Signal control")
    print()
    print("LED5: Green 2-Color, 5mm 3-pin, Milky lens")
    print()
    
    # Save files
    sch_path = os.path.join(output_dir, "BL520_Charger_generated.kicad_sch")
    bom_path = os.path.join(output_dir, "BL520_BOM_generated.md")
    net_path = os.path.join(output_dir, "BL520_Netlist_generated.txt")
    
    generator.save(sch_path)
    generate_bom(COMPONENTS, bom_path)
    generate_netlist(COMPONENTS, NETS, net_path)
    
    print()
    print("=" * 60)
    print("Generation completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
