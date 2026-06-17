//------------------------------------------------------------------------------------------------
// Part Base
//
// Base structure for a plate part. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;

//------------------------------------------------
// Part Constants
//------------------------------------------------
/* [Hidden] */

// Key for the type of a part
PART_TYPE = "part_type";

// Key for the name of the part
PART_NAME = "part_name";

// Key for the sub parts
SUB_PARTS = "sub-parts";

// Tag for subtraction 
REMOVE_TAG = "remove_tag";

//------------------------------------------------
// Functions
//------------------------------------------------

function part_base(type, name="", sub_parts=[]) = 
    struct_set([], [PART_TYPE, type, PART_NAME, name, SUB_PARTS, sub_parts]);

function is_part(part) = 
    in_list(PART_TYPE, struct_keys(part));

function part_type(part) = 
    assert(is_part(part))
    struct_val(part, PART_TYPE);

function part_name(part) = 
    assert(is_part(part))
    struct_val(part, PART_NAME);

function part_subparts(part) =
    assert(is_part(part))
    struct_value(part, SUB_PARTS, []);

function has_subparts(part) =
    len(part_subparts(part) > 0);
