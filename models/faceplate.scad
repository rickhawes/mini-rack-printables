include <BOSL2/std.scad>
include <BOSL2/fnliterals.scad>
include <./dimensions.scad>
include <./shapes.scad>

/* [Hidden] */
// Width of the tab hole found  (use 10-24 screw hole diameter for height)
shelf_tab_hole_width_tecmojo = 9.28; 

function layout_rack_screw_holes(
    rack_units,
    middle_holes = true,
    bottom_is_half_height = false
) = flatten(
        let (
            bottom_half_units = bottom_is_half_height ? 1 : 0,
            full_units = bottom_is_half_height ? floor(rack_units - 0.5) : floor(rack_units),
            top_half_units = rack_units - bottom_half_units*0.5 - full_units > 0 ? 1 : 0
        )
        [
            // Construct the y values for the holes from 0 to height
            //
            // bottom half units
            for(u = 0; u < bottom_half_units; u = u+1)
                if (middle_holes) 
                    [rack_screw_middle - rack_1u_height/2, rack_screw_top - rack_1u_height/2] 
                else
                    [rack_screw_top - rack_1u_height/2],
            
            // middle full units
            for(u = 0; u < full_units; u = u+1)
                let(y_slot = u*rack_1u_height + bottom_half_units*rack_1u_height/2)
                if (middle_holes)
                    [rack_screw_bottom+y_slot, rack_screw_middle+y_slot, rack_screw_top+y_slot]
                else
                    [rack_screw_bottom+y_slot, rack_screw_top+y_slot],
            
            // top half units 
            for(u = 0; u < top_half_units; u = u+1)
                let(y_slot = rack_1u_height*full_units + bottom_half_units*rack_1u_height/2)
                if (middle_holes)
                    [rack_screw_bottom+y_slot, rack_screw_middle+y_slot]
                else
                    [rack_screw_bottom+y_slot]
                 
        ]
    );

module rack_screw_holes(
    rack_units,
    faceplate_thickness, 
    middle_holes = true,
    bottom_is_half_height = false
) {
    assert(!is_undef(rack_units), "rack_units is undefined");
    height = rack_units * rack_1u_height;

    module one_hole(faceplate_thickness) {
        linear_extrude(height = faceplate_thickness) 
            slot_2d(shelf_tab_hole_width_tecmojo, screw_hole_10_24/2);
    }

    module right_tab() {
        translate([rack_screw_dx/2, -height/2, 0]) {
            y_values = layout_rack_screw_holes(rack_units, middle_holes, bottom_is_half_height);
            echo(y_values);
            for (y = y_values) {
                translate([0, y])
                    one_hole(faceplate_thickness);
            }
        }
    }

    right_tab();
    xflip()
        right_tab(); 
}

module blank_plate(height, faceplate_thickness) {
    linear_extrude(faceplate_thickness)
        rect([rack_width_10inch, height], rounding=3);
}

module faceplate(rack_units, faceplate_thickness, middle_holes = true, bottom_is_half_height = false) {
    height = rack_units * rack_1u_height;
    difference() {
        blank_plate(height, faceplate_thickness);
        rack_screw_holes(rack_units, faceplate_thickness, middle_holes, bottom_is_half_height);
    }
}