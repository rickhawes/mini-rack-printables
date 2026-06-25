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


//------------------------------------------------
// Functions
//------------------------------------------------

// Create an assembly base structure
function assembly_base(kind) = 
    struct_set([], [
        TYPE_KEY, ASSEMBLY_TYPE,
        SUBTYPE_KEY, kind
    ]);

// Is this structure an assembly type
function is_assembly(assembly) =
    is_struct(assembly) && struct_val(assembly, TYPE_KEY) == ASSEMBLY_TYPE;

// Create an part base structure
function part_base(kind) = 
    struct_set([], [
        TYPE_KEY, PART_TYPE,
        SUBTYPE_KEY, kind
    ]);

// Is this structure an assembly type
function is_part(part) =
    is_struct(part) && struct_val(part, TYPE_KEY) == PART_TYPE;

// Get the type from the base of the struct
function get_type(s) = 
    struct_val(s, TYPE_KEY);

// Get the subtype from the base of the struct
function get_subtype(s) =
    struct_val(s, SUBTYPE_KEY);
