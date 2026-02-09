#==============================================================================
# BL520 Charger Board V1.0 - OrCAD Capture TCL Script
# Robot Vacuum Charging Station
# 
# Usage: 
#   1. Open OrCAD Capture
#   2. Tools -> TCL -> Execute Script
#   3. Select this file (BL520_Charger.tcl)
#
# Note: This script requires OrCAD Capture 17.x or later
#==============================================================================

package require Tcl 8.5

# Global settings
set projectName "BL520_Charger"
set schematicName "BL520_Charger"
set pageSize "A3"

#------------------------------------------------------------------------------
# Component Data Structure
#------------------------------------------------------------------------------

# Format: {Reference Value Footprint X Y Rotation}
set components {
    {DC1 "DC_JACK" "CONN_PWR_JACK" 1000 1500 0}
    {D1 "SS34" "SMA" 1500 1400 0}
    {D2 "SS34" "SMA" 1500 1600 0}
    {L1 "10uH" "L_1206" 2000 1400 90}
    {L2 "10uH" "L_1206" 2000 1600 90}
    {L3 "CMC" "L_TOROID" 1000 2200 0}
    {R9 "10K" "R_1206" 1500 2200 0}
    {R10 "10K" "R_1206" 1700 2200 0}
    {C2 "100uF/35V" "CAP_RADIAL_6.3" 2500 1700 0}
    {C3 "10uF/35V" "CAP_RADIAL_5" 2700 1700 0}
    {C5 "100uF/35V" "CAP_RADIAL_6.3" 2900 1700 0}
    {U1 "AMS1117-5.0" "SOT223" 3500 1500 0}
    {C4 "10uF/16V" "CAP_RADIAL_5" 3200 1700 0}
    {C6 "10uF/16V" "CAP_RADIAL_5" 3800 1700 0}
    {C7 "100nF" "C_0805" 4000 1700 0}
    {LED1 "IR_RX" "LED_5MM" 1500 3000 270}
    {LED2 "IR_TX_940nm" "LED_5MM" 1800 3000 270}
    {LED3 "IR_RX" "LED_5MM" 2100 3000 270}
    {LED4 "IR_TX_940nm" "LED_5MM" 2400 3000 270}
    {LED5 "GREEN_2C_MILKY" "LED_5MM_3PIN" 2800 3000 0}
    {Q1 "NPN" "SOT89" 1500 3800 0}
    {Q3 "NPN" "SOT89" 1800 3800 0}
    {Q5 "NPN" "SOT89" 2100 3800 0}
    {Q7 "NPN" "SOT89" 2400 3800 0}
    {Q9 "NPN" "SOT89" 2700 3800 0}
    {Q2 "NPN" "SOT23" 1500 4400 0}
    {Q4 "NPN" "SOT23" 1800 4400 0}
    {Q6 "NPN" "SOT23" 2100 4400 0}
    {Q8 "NPN" "SOT23" 2400 4400 0}
    {Q10 "NPN" "SOT23" 2700 4400 0}
    {Q11 "NPN" "SOT23" 3000 4400 0}
    {R11 "1K" "R_0603" 1500 4000 90}
    {R12 "1K" "R_0603" 1800 4000 90}
    {R13 "1K" "R_0603" 2100 4000 90}
    {R14 "1K" "R_0603" 2400 4000 90}
    {R15 "1K" "R_0603" 2700 4000 90}
    {J1 "FPC_3PIN" "CONN_3P_2.54" 4500 1500 0}
    {CHARGE "2PIN" "CONN_2P_2.54" 4500 2000 0}
}

# Net connections
# Format: {NetName {Component.Pin Component.Pin ...}}
set nets {
    {VIN {DC1.1 D1.A D2.A}}
    {GND {DC1.2 C2.2 C3.2 C5.2 C4.2 C6.2 C7.2 U1.1 Q1.E Q2.E Q3.E Q4.E Q5.E Q6.E Q7.E Q8.E Q9.E Q10.E Q11.E J1.2 CHARGE.2}}
    {VIN_FILT {D1.K L1.1}}
    {VIN_FILT2 {L1.2 C2.1 C3.1 C5.1 C4.1 U1.3}}
    {+5V {U1.2 C6.1 C7.1 LED1.A LED2.A LED3.A LED4.A LED5.1 J1.1}}
    {IR_TX1 {LED2.K Q1.C}}
    {IR_TX2 {LED4.K Q3.C}}
    {Q1_BASE {R11.2 Q1.B}}
    {Q3_BASE {R12.2 Q3.B}}
    {Q5_BASE {R13.2 Q5.B}}
    {Q7_BASE {R14.2 Q7.B}}
    {Q9_BASE {R15.2 Q9.B}}
    {CHARGE_OUT {CHARGE.1}}
    {FPC_SIG {J1.3}}
}

#------------------------------------------------------------------------------
# Procedures
#------------------------------------------------------------------------------

proc log_msg {msg} {
    puts "BL520: $msg"
}

proc create_schematic_page {design pageName pageSize} {
    log_msg "Creating schematic page: $pageName"
    
    # Create new schematic page
    # Note: Actual OrCAD API calls would go here
    # This is a template showing the structure
    
    return 1
}

proc place_component {design ref value footprint x y rotation} {
    log_msg "Placing component: $ref ($value) at ($x, $y)"
    
    # OrCAD Capture API call to place component
    # DboTclHelper_PlaceSchematicInstance $design $ref $value $x $y $rotation
    
    return 1
}

proc create_wire {design netName pin1 pin2} {
    log_msg "Creating wire: $netName from $pin1 to $pin2"
    
    # OrCAD Capture API call to create wire
    # DboTclHelper_CreateWire $design $pin1 $pin2
    
    return 1
}

proc add_net_label {design netName x y} {
    log_msg "Adding net label: $netName at ($x, $y)"
    
    # OrCAD Capture API call to add net label
    # DboTclHelper_PlaceNetAlias $design $netName $x $y
    
    return 1
}

proc add_title_block {design title date rev} {
    log_msg "Adding title block: $title"
    
    # Add title block information
    puts "Title: $title"
    puts "Date: $date"
    puts "Revision: $rev"
    
    return 1
}

#------------------------------------------------------------------------------
# Main Script Execution
#------------------------------------------------------------------------------

proc main {} {
    global projectName schematicName pageSize components nets
    
    log_msg "=========================================="
    log_msg "BL520 Charger Board - OrCAD TCL Generator"
    log_msg "=========================================="
    
    # Get current design (requires OrCAD to be running with open design)
    # set design [GetActivePMDesign]
    
    # For standalone execution, we'll output the commands
    log_msg ""
    log_msg "Project: $projectName"
    log_msg "Schematic: $schematicName"
    log_msg "Page Size: $pageSize"
    log_msg ""
    
    # Title Block
    add_title_block "" "BL520 Charger Board V1.0" "2019-03-16" "1.2"
    
    log_msg ""
    log_msg "===== COMPONENTS ====="
    
    # Place all components
    foreach comp $components {
        lassign $comp ref value footprint x y rotation
        place_component "" $ref $value $footprint $x $y $rotation
    }
    
    log_msg ""
    log_msg "===== COMPONENT SUMMARY ====="
    log_msg "Total components: [llength $components]"
    
    # Count by type
    set count_conn 0
    set count_diode 0
    set count_inductor 0
    set count_cap 0
    set count_ic 0
    set count_led 0
    set count_trans 0
    set count_res 0
    
    foreach comp $components {
        set ref [lindex $comp 0]
        if {[string match "DC*" $ref] || [string match "J*" $ref] || [string match "CHARGE*" $ref]} {
            incr count_conn
        } elseif {[string match "D*" $ref] && ![string match "LED*" $ref]} {
            incr count_diode
        } elseif {[string match "L*" $ref]} {
            incr count_inductor
        } elseif {[string match "C*" $ref]} {
            incr count_cap
        } elseif {[string match "U*" $ref]} {
            incr count_ic
        } elseif {[string match "LED*" $ref]} {
            incr count_led
        } elseif {[string match "Q*" $ref]} {
            incr count_trans
        } elseif {[string match "R*" $ref]} {
            incr count_res
        }
    }
    
    log_msg "  Connectors:   $count_conn"
    log_msg "  Diodes:       $count_diode"
    log_msg "  Inductors:    $count_inductor"
    log_msg "  Capacitors:   $count_cap"
    log_msg "  ICs:          $count_ic"
    log_msg "  LEDs:         $count_led"
    log_msg "  Transistors:  $count_trans"
    log_msg "  Resistors:    $count_res"
    
    log_msg ""
    log_msg "===== NETS ====="
    
    # Create nets
    foreach net $nets {
        set netName [lindex $net 0]
        set pins [lindex $net 1]
        log_msg "Net: $netName -> $pins"
    }
    
    log_msg ""
    log_msg "===== TRANSISTOR PACKAGES ====="
    log_msg "Q1, Q3, Q5, Q7, Q9: SOT-89 (High Current IR LED Driver)"
    log_msg "Q2, Q4, Q6, Q8, Q10, Q11: SOT-23-3 (Signal Control)"
    
    log_msg ""
    log_msg "===== LED5 INFO ====="
    log_msg "LED5: Green 2-Color, 5mm 3-pin, Milky diffused lens"
    
    log_msg ""
    log_msg "=========================================="
    log_msg "Script execution completed!"
    log_msg "=========================================="
}

#------------------------------------------------------------------------------
# Run main procedure
#------------------------------------------------------------------------------
main

#==============================================================================
# OrCAD Capture Specific Commands (uncomment when running in OrCAD)
#==============================================================================

# # Get active design
# proc GetActivePMDesign {} {
#     set lStatus [DboTclHelper_Init]
#     if {$lStatus != 0} {
#         puts "Error initializing TCL helper"
#         return ""
#     }
#     
#     set lDesign [DboSession_GetActiveDesign]
#     return $lDesign
# }

# # Create new schematic page
# proc CreateSchematicPage {design pageName} {
#     set lRootBlock [$design GetRootBlock]
#     set lNewPage [$lRootBlock NewSchematicPage $pageName]
#     return $lNewPage
# }

# # Place instance on schematic
# proc PlaceInstance {page libPath partName refDes x y rotation} {
#     set lInstance [$page PlaceInstance $libPath $partName $refDes $x $y $rotation]
#     return $lInstance
# }

# # Create wire between two points
# proc CreateWire {page x1 y1 x2 y2} {
#     set lWire [$page CreateWire $x1 $y1 $x2 $y2]
#     return $lWire
# }

# # Place net alias
# proc PlaceNetAlias {page netName x y} {
#     set lAlias [$page PlaceNetAlias $netName $x $y]
#     return $lAlias
# }

#==============================================================================
# BOM Generation
#==============================================================================

proc generate_bom {} {
    global components
    
    puts ""
    puts "=============================================="
    puts "BL520 Charger Board V1.0 - Bill of Materials"
    puts "=============================================="
    puts ""
    puts [format "%-10s %-20s %-20s" "Reference" "Value" "Footprint"]
    puts [string repeat "-" 55]
    
    foreach comp $components {
        lassign $comp ref value footprint x y rotation
        puts [format "%-10s %-20s %-20s" $ref $value $footprint]
    }
    
    puts ""
    puts "Total Components: [llength $components]"
}

# Generate BOM
generate_bom

#==============================================================================
# End of Script
#==============================================================================
