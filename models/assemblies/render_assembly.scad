//------------------------------------------------------------------------------------------------
// Render an assembly
//
//------------------------------------------------------------------------------------------------
include <assembly_base.scad>
include <face_plate.scad>

// render an assembly based on its kind
module render_assembly(assembly) {
    assert(is_assembly(assembly));
    if (assembly_type(assembly) == FACE_PLATE_TYPE) {
        _render_face_plate(assembly);
    } else {
        assert(false, "render_assembly: unknown assembly kind");
    }
}