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
STYLE_PLAIN         = "plain";

function has_lip(style) = style == STYLE_FRONT_LIP || style == STYLE_BACK_LIP;

// lip dimensions
lip_radius      = 1.0;
lip_dz          = 1.0;

//------------------------------------------------
// Functions and modules
//------------------------------------------------
function holder(
    // Holder style
    style = STYLE_PLAIN,
    // Component size
    device_size = [0,0,0], 
    // Wall thickness
    wall_thickness = 3.0,
    // Wall rounding 
    wall_rounding = 0.5,
    // radius for puck styles
    puck_radius = 1.0,
    // part
    align = CENTER,
    padding = 0,
    shift = [0,0]
) = 
    assert(device_size.x >= 0 && device_size.y >= 0 && device_size.z, "holder: size must be non-negative")
    // TODO: Think about non-semmetrical padding and shifting on the layout size calculation
    let(layout_size = rc_size(apply_padding(rc(device_size), padding)))
    object(
        part_base(
            HOLDER_TYPE, 
            align, 
            padding, 
            shift, 
            layout_size=layout_size
        ),
        style = style,
        device_size = device_size,
        wall_thickness = wall_thickness,
        wall_rounding = wall_rounding,
        puck_radius = puck_radius
    );

function is_holder(s) = s.part_type == HOLDER_TYPE;

module _render_holder(part, plate_size) {
    assert(is_holder(part));
    device_size = part.device_size;
    wall_thickness = part.wall_thickness;
    wall_rounding = part.wall_rounding;
    puck_radius = part.puck_radius;
    style = part.style;

    //
    // Each sub-module stacks, position's on the top of the previous module.
    //

    module tube_holder() {
        tag("remove")
        cuboid(
            device_size, 
            anchor = BOTTOM,
            rounding = wall_rounding,
            edges = "Z"
        ) {
            position(TOP)
            children();
        }
    }

    module render_lip() {
        tag("remove")
        cuboid(
            [device_size.x-2*lip_radius, device_size.y-2*lip_radius, lip_dz], 
            anchor = BOTTOM,
            rounding = wall_rounding,
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
                device_size.x + 2*wall_thickness, 
                device_size.y + 2*wall_thickness, 
                device_size.z + (has_lip(style) ? lip_dz : 0)
            ], 
            anchor=BOTTOM,
            rounding = wall_rounding,
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


