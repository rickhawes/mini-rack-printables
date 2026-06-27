//------------------------------------------------------------------------------------------------
// Division
//
// A div is used to layout a section of a plate by evenly dividing the plate in either 
// the Horizontal or Verticle direction. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;

//------------------------------------------------
// Part Constants
//------------------------------------------------
/* [Hidden] */

// value for the type of a part
HDIV_TYPE       = "hdiv";
VDIV_TYPE       = "vdiv";

DIV_PARTS       = "parts";
DIV_PADDING     = "padding";


//------------------------------------------------
// Functions
//------------------------------------------------


//
// HDiv
//

function hdiv(parts = [], padding = 0) = struct_set(
    part_base(HDIV_TYPE), [
        DIV_PARTS, parts,
        DIV_PADDING, padding
    ]);


module _render_hdiv(part, section_size) {

}


function vdiv(parts = [], padding = 0) = struct_set(
    part_base(VDIV_TYPE), [
        DIV_PARTS, parts,
        DIV_PADDING, padding
    ]);
