//------------------------------------------------------------------------------------------------
// Render an assembly or a part
//
// Polymorphic functions and modules that all parts can do
//
//------------------------------------------------------------------------------------------------
include <base.scad>
include <rect_cutout.scad>
include <div.scad>

// Tag for subtraction 
REMOVE_TAG = "remove_tag";

// Render a part based on its type
module render_part(part, section_size) {
    assert(is_part(part));
    if (get_subtype(part) == RECT_CUTOUT_TYPE) { 
        _render_rect_cutout(part, section_size);
    } else if (get_subtype(part) == DIV_TYPE) {
        _render_div(part, section_size);    
    } else {
        assert(false, "unknown part type");
    }
}

