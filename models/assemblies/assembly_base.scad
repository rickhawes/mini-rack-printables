//------------------------------------------------------------------------------------------------
// Base
//
// Base structure for an assembly. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;

//------------------------------------------------
// Constants
//------------------------------------------------
/* [Hidden] */


// Key for TYPE
ASSEMBLY_KEY = "assembly_type";


//------------------------------------------------
// Functions
//------------------------------------------------

// 
// Assembly Base
//

// Create an assembly base structure
function assembly_base(kind) = struct_set([], [
        ASSEMBLY_KEY, kind,
    ]);

// Is this structure an assembly type
function is_assembly(assembly) = is_struct(assembly) && in_list(ASSEMBLY_KEY, struct_keys(assembly));

// Get the type from the base of the struct
function assembly_type(assembly) = struct_val(assembly, ASSEMBLY_KEY);


