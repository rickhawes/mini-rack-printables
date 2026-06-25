//------------------------------------------------------------------------------------------------
// Part Base
//
// Base structure for a plate part. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;

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
    is_object(part) && has_key(part, PART_TYPE_KEY);//------------------------------------------------------------------------------------------------
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

// Key for the sub parts
SUB_PARTS = "sub-parts";

// Key for the add_ribs option
ADD_RIBS = "add_ribs";

//------------------------------------------------
// Functions
//------------------------------------------------

function part_base(type, sub_parts=[]) = 
    struct_set([], [PART_TYPE, type, SUB_PARTS, sub_parts]);

function is_part(part) = 
    in_list(PART_TYPE, struct_keys(part));

function part_type(part) = 
    assert(is_part(part))
    struct_val(part, PART_TYPE);

function part_subparts(part) =
    assert(is_part(part))
    struct_value(part, SUB_PARTS, []);

function has_subparts(part) =
    len(part_subparts(part) > 0);

//------------------------------------------------
// Render Options
//------------------------------------------------
function render_options(add_ribs) = 
    struct_set([], [ADD_RIBS, add_ribs]);

function has_add_ribs(options) =
    struct_val(part, ADD_RIBS);
