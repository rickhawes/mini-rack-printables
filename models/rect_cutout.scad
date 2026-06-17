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
    object(base, [
        "size", size, 
        "margin", margin,
        "rounding", rounding,
        "rib_size", rib_size
    ]);

function is_rect_cutout(part) = 
    is_object(part) && part.type == RECT_CUTOUT;

function rect_cutout_layout_size(part) =
    assert(is_rect_cutout(part))
    let (
        bound = build_rect_with_offset(dx=part.size.x, dy=part.size.y),
        union_margin = union_margin(part.margin, part.rib_size.x)
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
//------------------------------------------------------------------------------------------------
// Rect Cutout 
//
// Base structure, functions and modules for a rectangle cutout plate part. The cutout has
// the options to have rounded corners, an boarder
//
//------------------------------------------------------------------------------------------------
include <part_base.scad>
include <layout.scad>

//------------------------------------------------
// Part Constants
//------------------------------------------------
/* [Hidden] */

// value for the type of a part
RECT_CUTOUT = "rect_cutout";

RECT_CUTOUT_BOUND = "rect_cutout_bound";

RECT_CUTOUT_MARGIN = "rect_cutout_margin";

RECT_CUTOUT_ROUNDING = "rect_cutout_rounding";


//------------------------------------------------
// Functions and modules
//------------------------------------------------
function rect_cutout(
    bound,
    margin = 0,
    rounding = 0
) = 
    assert(is_rect(bound))
    assert(is_margin(margin))
    let(base = part_base(RECT_CUTOUT))
    struct_set(base, [
        RECT_CUTOUT_BOUND, bound, 
        RECT_CUTOUT_MARGIN, margin,
        RECT_CUTOUT_ROUNDING, rounding
    ]);

function is_rect_cutout(part) =
    part_type(part) == RECT_CUTOUT;
    
function rect_cutout_bound(part) = 
    assert(is_rect_cutout(part))
    struct_val(part, RECT_CUTOUT_BOUND);

function rect_cutout_margin(part) = 
    assert(is_rect_cutout(part))
    struct_val(part, RECT_CUTOUT_MARGIN);

function rect_cutout_rounding(part) = 
    assert(is_rect_cutout(part))
    struct_val(part, RECT_CUTOUT_ROUNDING);

function rect_cutout_layout_bound(part) =
    assert(is_rect_cutout(part))
    let (
        margin = rect_cutout_margin(part),
        bound = rect_cutout_bound(part),
        centered_bound = grow_to_center(bound)
    )
    apply_margin(rect = centered_bound, margin = margin);

module render_rect_cutout(
    part,
    part_size,
    options
) {
    bound = rect_cutout_bound(part);
    off = rect_offset(bound);
    rounding = rect_cutout_rounding(part);
    
    tag("cutout")
        translate(v = [off.x, off.y, part_size.z/2]) 
            extruded_roundrect(size=[rect_dx(bound), rect_dy(bound), part_size.z], r=rounding, anchor=TOP);
}
