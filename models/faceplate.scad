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
            slot_2d(shelf_tab_hole_width_tecmojo, screw_hole_10_32/2);
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

// TODO: add consider using achors and primoids from BOSL2
module plate_ribs(
    plate_dim, 
    dx_tab, 
    rib_width = 2.5,
    rib_depth = 1.0
) {
    module rib(dx, dy, dz) {
        translate([0, dy/2, dz/2])
            rotate([90, 0, 0])
                linear_extrude(height = dy) 
                    trapezoid(w2=dx, h=dz, ang=30);
    }

    y_rib = (plate_dim.y-rib_width)/2;
    for(y = [y_rib, -y_rib])
        translate([0, y, plate_dim.z])
            rib(dx=plate_dim.x-2*dx_tab-4, dy=rib_width, dz=rib_depth);
}


module blank_plate(plate_dim) {
    linear_extrude(plate_dim.z)
        rect([plate_dim.x, plate_dim.y], rounding=3);
}


module faceplate(rack_units, faceplate_thickness, middle_holes = true, bottom_is_half_height = false, add_ribs = true) {
    height = rack_units * rack_1u_height;
    plate_dim = [rack_width_10inch, height, faceplate_thickness];
    difference() {
        union() {
            blank_plate(plate_dim);
            if (add_ribs) {
                plate_ribs(plate_dim, shelf_tab_width_tecmojo);
            }
        }

        rack_screw_holes(rack_units, faceplate_thickness, middle_holes, bottom_is_half_height);
    }
}