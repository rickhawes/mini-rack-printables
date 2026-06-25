//------------------------------------------------------------------------------------------------
// Render an assembly
//
//------------------------------------------------------------------------------------------------
include <assembly_base.scad>
include <face_plate.scad>

// render an assembly based on its kind
module render_assembly(assembly) {
    assert(is_assembly(assembly));
    if (assembly.kind == FACE_PLATE_KIND) {
        _render_face_plate(assembly);
    } else {
        assert(false, "unknown assembly kind");
    }
}