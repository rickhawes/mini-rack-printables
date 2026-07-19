//------------------------------------------------------------------------------------------------
// Base
//
// Base object for a part description. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;

//------------------------------------------------
// Constants
//------------------------------------------------
/* [Hidden] */


//------------------------------------------------
// Functions
//------------------------------------------------

// Create an part base structure
function part_base(
    part_type, 
    align=CENTER, 
    padding=0, 
    shift=[0,0],
    layout_size=[0,0]
) = 
    object(
        part_type = part_type,
        align = align,
        padding = padding,
        shift = shift,
        layout_size = layout_size
    );

function is_part(part) = has_key(part, "part_type");

