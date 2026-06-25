//------------------------------------------------------------------------------------------------
// Render an assembly or a part
//
// Polymorphic functions and modules that all parts can do
//
//------------------------------------------------------------------------------------------------
include <part_base.scad>
include <rect_cutout.scad>

// Render a part based on its type
module render_part(part, section_size) {
    assert(is_part(part));
    if (part.type == RECT_CUTOUT) { 
        render_rect_cutout(part, section_size);
    } else {
        assert(false, "unknown part type");
    }
}