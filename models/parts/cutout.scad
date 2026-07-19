//------------------------------------------------------------------------------------------------
// Cutout 
//
// Structures, functions and modules for a cutout plate part. 
// Based on the size and radius paramater, the cutout can be a 
// a cicrular cutout, a slotted cutout, or a rounded rectangle cutout. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>
include <../geometry.scad>
include <../shapes.scad>
include <part_base.scad>

//------------------------------------------------
// Part Constants
//------------------------------------------------
/* [Hidden] */

// value for the type of a part
CUTOUT_TYPE     = "cutout";

//------------------------------------------------
// Functions and modules
//------------------------------------------------
function cutout(
    rect_size = [0,0],
    radius = 0,
    rib_size = [0,0],
    align = CENTER,
    padding = 0,
    shift = [0,0]
) = 
    assert(rect_size.x >= 0 && rect_size.y >= 0 && radius >= 0, "cutout: rect_size and radius must be non-negative")
    assert(is_padding(padding))
    let(
        cutout_rc = rc(rect_size),
        outset_rc = apply_padding(cutout_rc, radius),
        layout_rc = apply_padding(outset_rc, rib_size.x),
        base = part_base(
            CUTOUT_TYPE, 
            align, 
            padding, 
            shift, 
            layout_size=rc_size(layout_rc)
        )   
    )
    object(base, 
        rect_size = rect_size,
        radius = radius,
        rib_size = rib_size
    );

function is_cutout(part)    = part.part_type == CUTOUT_TYPE;

// Render the part in the context of an assembly
module _render_cutout(part, section_size) {
    assert(is_cutout(part), "part is not a cutout");
    rect_size       = part.rect_size;
    radius          = part.radius;
    rib_size        = part.rib_size;

    module outline_cutout(rect_size, radius) {
        if (radius == 0) {
            rect(size=rect_size);
        } else if (rect_size.x == 0 && rect_size.y == 0) {
            circle(r=radius); 
        } else if (rect_size.x == 0) {
            slot_yaxis(dy=rect_size.y+2*radius, r=radius);
        } else if (rect_size.y == 0) {
            slot_xaxis(dx=rect_size.x+2*radius, r=radius);
        } else {
            offset(r=radius) {
                rect(size=rect_size);
            }
        }
    }
    
    // Cutout
    position(BOTTOM)
    tag("remove")
    linear_extrude(height=section_size.z) {
        outline_cutout(rect_size=rect_size, radius=radius);    
    }    
    
    // Rib around the cutout
    if (rib_size.x > 0 && rib_size.y > 0) {
        tag("keep")
        position(TOP)
        extrude_rib(rib_size) {
            outline_cutout(rect_size=rect_size, radius=radius);
        }
    }
}
