//------------------------------------------------------------------------------------------------
// STL 
//
// Structures, functions and modules for a STL import based plate part. 
// Must measure the size of the STL file and provide it as 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>
include <../geometry.scad>
include <../shapes.scad>
include <part_base.scad>

//------------------------------------------------
// Part Constants
//------------------------------------------------
/* [Hidden] */

// value for the type of a part
STL_TYPE        = "stl";
STL_FILE        = "file";
STL_SIZE        = "size";
STL_ADJUST      = "adjust";


//------------------------------------------------
// Functions and modules
//------------------------------------------------
function stl(
    file = "",
    size = [0,0],
    center_adjust = [0,0,0],
    align = CENTER,
    padding = 0,
    shift = [0,0]
) = 
    assert(size.x >= 0 && size.y >= 0, "stl: size must be non-negative")
    struct_set(
        part_base(
            STL_TYPE, 
            align, 
            padding, 
            shift, 
            layout_size=size
        ), [
        STL_FILE, file,
        STL_SIZE, size,
        STL_ADJUST, center_adjust
    ]);

function is_stl(s) = is_struct(s) && part_type(s) == STL_TYPE;
function stl_file(s) = struct_val(s, STL_FILE);
function stl_size(s) = struct_val(s, STL_SIZE);
function stl_adjust(s) = struct_val(s, STL_ADJUST);


module _render_stl(part, plate_size) {
    assert(is_stl(part));
    size = stl_size(part);
    file_name = stl_file(part);
    adjust = stl_adjust(part);
    
    tag("remove")
    translate([0,0,-plate_size.z])
    cuboid(size);

    tag("keep")
    translate([
        adjust.x, 
        adjust.y, 
        size.z/2 - plate_size.z + adjust.z
    ]) {
        import(file_name, center=true);
    }
}


