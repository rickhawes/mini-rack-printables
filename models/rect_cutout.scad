//------------------------------------------------------------------------------------------------
// Rect Cutout 
//
// Base structure, functions and modules for a rectangle cutout plate part. The cutout has
// the options to have rounded corners, an boarder
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>
include <base.scad>
include <geometry.scad>
include <shapes.scad>

//------------------------------------------------
// Part Constants
//------------------------------------------------
/* [Hidden] */

// value for the type of a part
RECT_CUTOUT_TYPE = "rect_cutout";

RC_SIZE         = "size";
RC_PADDING      = "padding";
RC_ROUNDING     = "rounding";
RC_RIB_SIZE     = "rib_size";

//------------------------------------------------
// Functions and modules
//------------------------------------------------
function rect_cutout(
    size,
    padding = 0,
    rounding = 0,
    rib_size = undef
) = 
    assert(size.x > 0 && size.y > 0)
    assert(is_padding(padding))
    let(base = part_base(RECT_CUTOUT_TYPE))
    struct_set(base, [
        RC_SIZE, size,
        RC_PADDING, padding,
        RC_ROUNDING, rounding,
        RC_RIB_SIZE, rib_size
    ]);

function is_rect_cutout(part) = 
    get_subtype(part) == RECT_CUTOUT_TYPE;

function rc_size(rc) = struct_val(rc, RC_SIZE);
function rc_padding(rc) = struct_val(rc, RC_PADDING);
function rc_rounding(rc) = struct_val(rc, RC_ROUNDING);
function rc_rib_size(rc) = struct_val(rc, RC_RIB_SIZE);

// layout function
function rect_cutout_layout_size(part) =
    assert(is_rect_cutout(part))
    let (
        bound = build_rect_with_offset(dx=part.size.x, dy=part.size.y),
        union_padding = union_padding(part.padding, part.rib_size.x)
    )
    apply_padding(rect = bound, padding = union_padding);

// Render the part in the context of an assembly
module _render_rect_cutout(part, section_size) {
    cutout_size     = rc_size(part);
    rounding        = rc_rounding(part);
    rib_size        = rc_rib_size(part);
    
    // Cutout
    tag(REMOVE_TAG)
        position(BOTTOM)
            extruded_roundrect(size=[cutout_size.x, cutout_size.y, section_size.z], r=rounding, anchor=BOTTOM);
    
    // Rib around the cutout
    if (!is_undef(rib_size)) {
        position(TOP)
        extrude_rib(rib_size) {
            rect(size=cutout_size, rounding=rounding);
        }
    }
}
