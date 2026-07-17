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
HOLDER_TYPE     = "hold";
HOLD_SIZE       = "size";
HOLD_ROUNDING   = "rounding";
HOLD_THICKNESS  = "thickness";
HOLD_STYLE      = "style";

STYLE_FRONT_LIP     = "front_lip";
STYLE_BACK_LIP      = "back_lip";
SYTLE_PLAIN         = "no_lip";

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
    struct_set(
        part_base(
            HOLDER_TYPE, 
            align, 
            padding, 
            shift, 
            layout_size=layout_size
        ), [
        HOLD_SIZE, size,
        HOLD_ROUNDING, rounding,
        HOLD_THICKNESS, thickness,
        HOLD_STYLE, style
    ]);

function is_holder(s)       = is_struct(s) && part_type(s) == HOLDER_TYPE;
function hold_size(s)       = struct_val(s, HOLD_SIZE);
function hold_rounding(s)   = struct_val(s, HOLD_ROUNDING);
function hold_thickness(s)  = struct_val(s, HOLD_THICKNESS);
function hold_sytle(s)      = struct_val(s, HOLD_STYLE);


module _render_holder(part, plate_size) {
    assert(is_holder(part));
    size = hold_size(part);
    rounding = hold_rounding(part);
    thickness = hold_thickness(part);
    style = hold_sytle(part);

    //
    // Each sub-module stacks, position's on the top of the previous module.
    //

    module main_holder() {
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
            main_holder();
        } else if (style == STYLE_BACK_LIP) {
            main_holder()
            render_lip();
        } else {
            assert(lip == STYLE_PLAIN);
            main_holder();
        }
    }
}


