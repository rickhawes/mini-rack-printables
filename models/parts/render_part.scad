//------------------------------------------------------------------------------------------------
// Render an assembly or a part
//
// Polymorphic functions and modules that all parts can do
//
//------------------------------------------------------------------------------------------------
include <part_base.scad>
include <cutout.scad>
include <div.scad>
include <stl.scad>
include <keystone.scad>
include <holder.scad>

// Render a part based on its type
module render_part(part, plate_size) {
    assert(is_part(part));
    if (part.part_type == CUTOUT_TYPE) { 
        _render_cutout(part, plate_size);
    } else if (part.part_type == DIV_TYPE) {
        _render_div(part, plate_size);    
    } else if (part.part_type == STL_TYPE) {
        _render_stl(part, plate_size);
    } else if (part.part_type == KEYSTONE_TYPE) {
        _render_keystone(part, plate_size);
    } else if (part.part_type == HOLDER_TYPE) {
        _render_holder(part, plate_size);
    } else {
        assert(false, "render_part: unknown part type");
    }
}


