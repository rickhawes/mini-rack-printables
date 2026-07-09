//------------------------------------------------------------------------------------------------
// Base
//
// Base structure for an assembly and part description. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;

//------------------------------------------------
// Constants
//------------------------------------------------
/* [Hidden] */

// Key for TYPE
PART_TYPE_KEY = "part_type";

// Key for _padding_
PADDING_KEY = "padding";

// Key for align
ALIGN_KEY = "align";

// Key for _shift_
SHIFT_KEY = "shift";

// Key for layout_size
LAYOUT_SIZE_KEY = "layout_size";


//------------------------------------------------
// Functions
//------------------------------------------------

// Create an part base structure
function part_base(
    kind, 
    align=CENTER, 
    padding=0, 
    shift=[0,0],
    layout_size=[0,0]
) = 
    struct_set([], [
        PART_TYPE_KEY, kind,
        ALIGN_KEY, align,
        PADDING_KEY, padding,
        SHIFT_KEY, shift,
        LAYOUT_SIZE_KEY, layout_size
    ]);

// Get the type from the base of the struct
function part_type(s) = struct_val(s, PART_TYPE_KEY);

// Is this structure an assembly type
function is_part(part) = is_struct(part) && in_list(PART_TYPE_KEY, struct_keys(part));

// How to align the part (uses BOLS2 values)
function part_align(part) = 
    assert(is_part(part))
    struct_val(part, ALIGN_KEY);

// Padding to add to the parts layout. Maybe a number, a [dx, dy] or a [right, left, top, bottom]
function part_padding(part) = 
    assert(is_part(part))
    struct_val(part, PADDING_KEY);

// A [x,y] shift to the center of the part
function part_shift(part) = 
    assert(is_part(part))
    struct_val(part, SHIFT_KEY);

// The size of the part for layout purposes. 
function part_layout_size(part) = 
    assert(is_part(part))
    struct_val(part, LAYOUT_SIZE_KEY);