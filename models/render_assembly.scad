//------------------------------------------------------------------------------------------------
// Render an assembly
//
//------------------------------------------------------------------------------------------------
include <base.scad>
include <face_plate.scad>

// render an assembly based on its kind
module render_assembly(assembly) {
    assert(is_assembly(assembly));
    if (get_subtype(assembly) == FACE_PLATE_TYPE) {
        _render_face_plate(assembly);
    } else {
        assert(false, "unknown assembly kind");
    }
}