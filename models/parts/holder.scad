//------------------------------------------------------------------------------------------------
// Holder 
//
// Structures, functions and modules for device holder part. 
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
HOLDER_TYPE         = "holder";

// Holder styles
STYLE_FRONT_LIP     = "front_lip";
STYLE_BACK_LIP      = "back_lip";
STYLE_PUCK          = "puck";
SYTLE_PLAIN         = "plain";

function has_lip(style) = style == STYLE_FRONT_LIP || style == STYLE_BACK_LIP;

// lip dimensions
lip_radius      = 1.0;
lip_dz          = 1.0;


//------------------------------------------------
// Functions and modules
//------------------------------------------------
function holder(
    size = [0,0,0],
    rounding = 0.5,
    thickness = 3.0,
    style = STYLE_PLAIN,
    align = CENTER,
    padding = 0,
    shift = [0,0]
) = 
    assert(size.x >= 0 && size.y >= 0 && size.z, "holder: size must be non-negative")
    // TODO: Think about non-semmetrical padding and shifting on the layout size calculation
    let(layout_size = rc_size(apply_padding(rc(size), padding)))
    object(
        part_base(
            HOLDER_TYPE, 
            align, 
            padding, 
            shift, 
            layout_size=layout_size
        ),
        size = size,
        rounding = rounding,
        thickness = thickness,
        style = style
    );

function is_holder(s)       = s.part_type == HOLDER_TYPE;

module _render_holder(part, plate_size) {
    assert(is_holder(part));
    size = part.size;
    rounding = part.rounding;
    thickness = part.thickness;
    style = part.style;

    //
    // Each sub-module stacks, position's on the top of the previous module.
    //

    module tube_holder() {
        tag("remove")
        cuboid(
            size, 
            anchor = BOTTOM,
            rounding = rounding,
            edges = "Z"
        ) {
            position(TOP)
            children();
        }
    }

    module render_lip() {
        tag("remove")
        cuboid(
            [size.x-2*lip_radius, size.y-2*lip_radius, lip_dz], 
            anchor = BOTTOM,
            rounding = rounding,
            edges = "Z"
        ) {
            position(TOP)
            children();
        }
    }

    position(BOTTOM) {
        // Shell
        cuboid(
            [
                size.x + 2*thickness, 
                size.y + 2*thickness, 
                size.z + (has_lip(style) ? lip_dz : 0)
            ], 
            anchor=BOTTOM,
            rounding = rounding,
            edges = [TOP, FRONT, RIGHT, BACK, LEFT]
        );

        // remove parts
        if (style == STYLE_FRONT_LIP) {
            render_lip()
            tube_holder();
        } else if (style == STYLE_BACK_LIP) {
            tube_holder()
            render_lip();
        } else {
            assert(lip == STYLE_PLAIN);
            tube_holder();
        }
    }
}


