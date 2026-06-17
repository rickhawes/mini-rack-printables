//------------------------------------------------------------------------------------------------
// Part Dispatch
//
// Polymorphic functions and modules that all parts can do
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;
include <part_base.scad>;
include <rect_cutout.scad>;

//------------------------------------------------
// Parts
//------------------------------------------------

// Render the part tree
// 

module render_parts(part, section_size) {
    assert(is_part(part));
    type = part_type(part);
    if (type == RECT_CUTOUT) { 
        render_rect_cutout(part, section_size);
    } else {
        assert(false, "unknown part type");
    }
}