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
TYPE_KEY = "type";

// Key for subtype
SUBTYPE_KEY = "subtype";

// Type for assemblies
ASSEMBLY_TYPE = "assembly";

// Type for parts
PART_TYPE = "part";

// Key for _padding_
PADDING_KEY = "padding";

// Key for align
ALIGN_KEY = "align";

// Key for _shift_
SHIFT_KEY = "shift";


//------------------------------------------------
// Functions
//------------------------------------------------

// Get the type from the base of the struct
function get_type(s) = 
    struct_val(s, TYPE_KEY);

// Get the subtype from the base of the struct
function get_subtype(s) =
    struct_val(s, SUBTYPE_KEY);


// 
// Assembly Base
//

// Create an assembly base structure
function assembly_base(kind) = 
    struct_set([], [
        TYPE_KEY, ASSEMBLY_TYPE,
        SUBTYPE_KEY, kind
    ]);

// Is this structure an assembly type
function is_assembly(assembly) =
    is_struct(assembly) && struct_val(assembly, TYPE_KEY) == ASSEMBLY_TYPE;


//
// Part Base
//

// Create an part base structure
function part_base(
    kind, 
    align=CENTER, 
    padding=0, 
    shift=[0,0]
) = 
    struct_set([], [
        TYPE_KEY, PART_TYPE,
        SUBTYPE_KEY, kind,
        ALIGN_KEY, align,
        PADDING_KEY, padding,
        SHIFT_KEY, shift
    ]);

// Is this structure an assembly type
function is_part(part) =
    is_struct(part) && struct_val(part, TYPE_KEY) == PART_TYPE;

// How to align the part (uses BOLS2 values)
function get_align(part) = 
    assert(is_part(part))
    struct_val(part, ALIGN_KEY);

// Padding to add to the parts layout. Maybe a number, a [dx, dy] or a [right, left, top, bottom]
function get_padding(part) = 
    assert(is_part(part))
    struct_val(part, PADDING_KEY);

// A [x,y] shift to the center of the part
function get_shift(part) = 
    assert(is_part(part))
    struct_val(part, SHIFT_KEY);