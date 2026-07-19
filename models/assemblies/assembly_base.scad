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
function assembly_base(type) = object(assembly_type = type);

// Is this structure an assembly type
function is_assembly(assembly) = has_key(assembly, ASSEMBLY_KEY);

