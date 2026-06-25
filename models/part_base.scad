//------------------------------------------------------------------------------------------------
// Part Base
//
// Base structure for a plate part. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>

//------------------------------------------------
// Constants
//------------------------------------------------
/* [Hidden] */

// Tag for subtraction 
REMOVE_TAG = "remove_tag";

// KEY for PART_TYPE
PART_TYPE_KEY = "type";

//------------------------------------------------
// Functions
//------------------------------------------------

function part_base(type, sub_parts=[]) = 
    object([
        [PART_TYPE_KEY, type],
        ["sub_parts", sub_parts]
    ]);

function is_part(part) =
    is_object(part) && has_key(part, PART_TYPE_KEY);
  