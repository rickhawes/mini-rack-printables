//------------------------------------------------------------------------------------------------
// Assembly base
//
// Base structure for an assembly description. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;

//------------------------------------------------
// Constants
//------------------------------------------------
/* [Hidden] */

ASSEMBLY_KIND_KEY = "kind";

//------------------------------------------------
// Functions
//------------------------------------------------

function assembly_base(kind) = 
    object([
        [ASSEMBLY_KIND_KEY, kind]
    ]);

function is_assembly(assembly) =
    is_object(assembly) && has_key(assembly, ASSEMBLY_KIND_KEY);
