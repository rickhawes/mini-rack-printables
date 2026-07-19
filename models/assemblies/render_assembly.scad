//------------------------------------------------------------------------------------------------
// Render an assembly
//
//------------------------------------------------------------------------------------------------
include <face_plate.scad>

// render an assembly based on its kind
module render_assembly(assembly) {
    if (assembly.assembly_type == FACE_PLATE_TYPE) {
        _render_face_plate(assembly);
    } else {
        assert(false, "render_assembly: unknown assembly kind");
    }
}
