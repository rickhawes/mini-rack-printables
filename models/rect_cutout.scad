//------------------------------------------------------------------------------------------------
// Rect Cutout 
//
// Base structure, functions and modules for a rectangle cutout plate part. The cutout has
// the options to have rounded corners, an boarder
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>
include <part_base.scad>
include <layout.scad>

//------------------------------------------------
// Part Constants
//------------------------------------------------
/* [Hidden] */

// value for the type of a part
RECT_CUTOUT = "rect_cutout";

RECT_CUTOUT_SIZE = "rect_cutout_size";

RECT_CUTOUT_MARGIN = "rect_cutout_margin";

RECT_CUTOUT_ROUNDING = "rect_cutout_rounding";

RECT_CUTOUT_RIB_SIZE = "rect_cutout_rib_size";


//------------------------------------------------
// Functions and modules
//------------------------------------------------
function rect_cutout(
    size,
    margin = 0,
    rounding = 0,
    name = "",
    rib_size = undef
) = 
    assert(size.x > 0 && size.y > 0)
    assert(is_margin(margin))
    let(base = part_base(RECT_CUTOUT, name=name))
    struct_set(base, [
        RECT_CUTOUT_SIZE, size, 
        RECT_CUTOUT_MARGIN, margin,
        RECT_CUTOUT_ROUNDING, rounding,
        RECT_CUTOUT_RIB_SIZE, rib_size
    ]);

function is_rect_cutout(part) =
    part_type(part) == RECT_CUTOUT;
    
function rect_cutout_size(part) = 
    assert(is_rect_cutout(part))
    struct_val(part, RECT_CUTOUT_SIZE);

function rect_cutout_margin(part) = 
    assert(is_rect_cutout(part))
    struct_val(part, RECT_CUTOUT_MARGIN);

function rect_cutout_rounding(part) = 
    assert(is_rect_cutout(part))
    struct_val(part, RECT_CUTOUT_ROUNDING);

function rect_cutout_rib_size(part) =
    assert(is_rect_cutout(part))
    struct_val(part, RECT_CUTOUT_RIB_SIZE);

function rect_cutout_layout_size(part) =
    assert(is_rect_cutout(part))
    let (
        margin = rect_cutout_margin(part),
        size = rect_cutout_size(part),
        bound = build_rect_with_offset(dx=size.x, dy=size.y),
        rib_size = rect_cutout_rib(part),
        union_margin = union_margin(margin, rib_size.x)
    )
    apply_margin(rect = bound, margin = union_margin);

module render_rect_cutout(
    part,
    part_size,
    options
) {
    cutout_size = rect_cutout_size(part);
    rounding = rect_cutout_rounding(part);
    rib_size = rect_cutout_rib_size(part);
    
    // Cutout
    tag(REMOVE_TAG)
        position(BOTTOM)
            extruded_roundrect(size=[cutout_size.x, cutout_size.y, part_size.z], r=rounding, anchor=BOTTOM);
    
    // Rib around the cutout
    if (!is_undef(rib_size)) {
        position(TOP)
        extrude_rib(rib_size) {
            rect(size=cutout_size, rounding=rounding);
        }
    }
}
