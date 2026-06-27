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
    rounding = 0,
    rib_size = [0,0],
    align = CENTER,
    padding = 0,
    shift = [0,0]
) = 
    assert(size.x > 0 && size.y > 0)
    assert(is_padding(padding))
    let(
        cutout_rc = rc(size),
        layout_rc = apply_padding(cutout_rc, rib_size.x),
        base = part_base(
            RECT_CUTOUT_TYPE, 
            align, 
            padding, 
            shift, 
            layout_size=rc_size(layout_rc)
        )   
    )
    struct_set(base, [
        CO_SIZE, size,
        CO_ROUNDING, rounding,
        CO_RIB_SIZE, rib_size
    ]);

function is_rect_cutout(part) = 
    get_subtype(part) == RECT_CUTOUT_TYPE;

function co_size(co) = struct_val(co, CO_SIZE);
function co_rounding(co) = struct_val(co, CO_ROUNDING);
function co_rib_size(co) = struct_val(co, CO_RIB_SIZE);


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
