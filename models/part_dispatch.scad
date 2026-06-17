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


module render_parts(part, part_size, options) {
    assert(is_part(part));
    type = part_type(part);
    if (type == RECT_CUTOUT) { 
        render_rect_cutout(part, part_size, options);
    } else {
        assert(false, "unknown part type");
    }
}