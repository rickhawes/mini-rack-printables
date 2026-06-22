//------------------------------------------------------------------------------------------------
// Render an assembly or a part
//
// Polymorphic functions and modules that all parts can do
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;
include <part_base.scad>;
include <rect_cutout.scad>;
include <face_plate.scad>;


module _render_parts(part, section_size) {
    assert(is_part(part));
    if (part.type == RECT_CUTOUT) { 
        render_rect_cutout(part, section_size);
    } else {
        assert(false, "unknown part type");
    }
}

module render_assembly(assembly) {
    assert(is_assembly(assembly));
    if (assembly.kind == FACE_PLATE_KIND) {
        _render_faceplate(assembly);
    } else {
        assert(false, "unknown assembly kind");
    }
}