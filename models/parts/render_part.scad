//------------------------------------------------------------------------------------------------
// Render an assembly or a part
//
// Polymorphic functions and modules that all parts can do
//
//------------------------------------------------------------------------------------------------
include <part_base.scad>
include <cutout.scad>
include <div.scad>

// Render a part based on its type
module render_part(part, plate_size, subtraction = false) {
    assert(is_part(part));
    if (part_type(part) == CUTOUT_TYPE) { 
        _render_cutout(part, plate_size, subtraction);
    } else if (part_type(part) == DIV_TYPE) {
        _render_div(part, plate_size, subtraction);    
    } else {
        assert(false, "render_part: unknown part type");
    }
}

// with_part_rendering is a helper module that renders a part and then executes the given code block
module with_part_rendering(part, part_area_size) {
    difference() {
        union() {
            // Render the plate
            children();

            // Render the part additions 
            if (!is_undef(part)) {
                render_part(part = part, plate_size = part_area_size, subtraction = false);
            }
        }

        // Render the part subtractions 
        if (!is_undef(part)) {
            render_part(part = part, plate_size = part_area_size, subtraction = true);
        }
    }
}
