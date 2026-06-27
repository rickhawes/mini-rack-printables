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

CO_SIZE         = "size";
CO_PADDING      = "padding";
CO_ROUNDING     = "rounding";
CO_RIB_SIZE     = "rib_size";

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
        CO_SIZE, size,
        CO_PADDING, padding,
        CO_ROUNDING, rounding,
        CO_RIB_SIZE, rib_size
    ]);

function is_rect_cutout(part) = 
    get_subtype(part) == RECT_CUTOUT_TYPE;

function co_size(rc) = struct_val(rc, CO_SIZE);
function co_padding(rc) = struct_val(rc, CO_PADDING);
function co_rounding(rc) = struct_val(rc, CO_ROUNDING);
function co_rib_size(rc) = struct_val(rc, CO_RIB_SIZE);

// Calculate the layout size including ribs for the part
function rect_cutout_layout_size(rc) =
    assert(is_rect_cutout(rc))
    let(
        size = rc_size(rc),
        rib_size = co_rib_size(rc),
        rib_padding = rib_size.x,
        cutout_rc = rc_from_size(size),
        layout_rc = apply_padding(cutout_rc, rib_padding)
    )
    rc_size(layout_rc);

// Render the part in the context of an assembly
module _render_rect_cutout(part, section_size) {
    cutout_size     = co_size(part);
    rounding        = co_rounding(part);
    rib_size        = co_rib_size(part);
    
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
