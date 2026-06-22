include <BOSL2/std.scad>
include <./dimensions.scad>
include <./shapes.scad>
include <./part_dispatch.scad>

//------------------------------------------------------------------------------------------------
// Face Plate 
//
// Modules to render a face plate assembly 
//
//------------------------------------------------------------------------------------------------

/* [Hidden] */
// Width of the tab hole found  (use 10-24 screw hole diameter for height)
shelf_tab_hole_width_tecmojo = 9.28; 
// Rounding applied to corners of a faceplate
faceplate_rounding = 3.0;

FACE_PLATE_KIND = "face_plate";

function face_plate(
    rack_units, 
    face_plate_thickness, 
    middle_holes = true, 
    bottom_is_half_height = false, 
    rib_size,
    part
) = object(
    assembly_base(FACE_PLATE_KIND), 
    [
        ["rack_units", rack_units],
        ["face_plate_thinkness", face_plate_thickness],
        [middle_holes],
        [bottom_is_half_height],
        [rib_size],
        [part]
    ]
);

function is_face_plate(plate) = 
    is_object(plate) && plate.kind == FACE_PLATE_KIND;


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


module _render_faceplate(face_plate) {
    rack_units = face_plate.rack_units;
    faceplate_thickness = face_plate.faceplate_thickness;
    middle_holes = face_plate.middle_holes;
    bottom_is_half_height = face_plate.bottom_is_half_height;
    rib_size = face_plate.rib_size;
    part = face_plate.part; 

    module rack_screw_holes(
        rack_units,
        faceplate_thickness, 
        middle_holes = true,
        bottom_is_half_height = false
    ) {
        assert(!is_undef(rack_units), "rack_units is undefined");
        height = rack_units * rack_1u_height;

        module one_hole(faceplate_thickness) {
            attachable() {
                linear_extrude(height = faceplate_thickness) 
                    slot_xaxis(shelf_tab_hole_width_tecmojo, screw_hole_10_32/2);
                children();
            }
        }

        module right_tab() {
            translate([rack_screw_dx/2, -height/2, 0]) {
                y_values = layout_rack_screw_holes(rack_units, middle_holes, bottom_is_half_height);
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

    module faceplate_ribs(plate_size, part_size, rib_size) {
        tag("rib") 
        align(TOP, [FRONT,BACK]) 
            prismoid(size2=[part_size.x, rib_size.x], h=rib_size.y, xang=30, yang=90);
    }

    // Layout calculations
    height = rack_units * rack_1u_height;
    plate_size = [rack_width_10inch, height, faceplate_thickness];
    part_area_width = plate_size.x - 2*shelf_tab_width_tecmojo - 2*rib_size.x;
    part_area_height = plate_size.y - 2*rib_size.x;
    part_area_size = [part_area_width, part_area_height, faceplate_thickness];

    diff(remove=REMOVE_TAG) {
        extruded_roundrect(plate_size, r = faceplate_rounding, anchor=TOP) {
            // Ribs on top and bottoms 
            if (!is_undef(rib_size)) {
                faceplate_ribs(plate_size, part_area_size, rib_size);
            }
 
            // Rack Screw
            tag(REMOVE_TAG) align(BOTTOM) {
                rack_screw_holes(rack_units, faceplate_thickness, middle_holes, bottom_is_half_height);
            }

            // Parts
            if (!is_undef(part)) {
                _render_part(part = part, section_size = parts_area_size);
            }
        }
    }
}