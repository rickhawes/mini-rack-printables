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

//------------------------------------------------
// Functions and modules
//------------------------------------------------
STL_TYPE = "stl";

function stl(
    file = "",
    size = [0,0],
    center_adjust = [0,0,0],
    align = CENTER,
    padding = 0,
    shift = [0,0]
) =
    assert(size.x >= 0 && size.y >= 0, "stl: size must be non-negative")
    object(
        part_base(
            STL_TYPE,
            align,
            padding,
            shift,
            layout_size=size
        ),
        file = file,
        size = size,
        center_adjust = center_adjust
    );

function is_stl(part) = part.part_type == STL_TYPE;

module _render_stl(part, plate_size) {
    assert(is_stl(part));

    tag("remove")
    translate([0,0,-plate_size.z])
    cuboid(part.size);

    tag("keep")
    translate([
        part.center_adjust.x,
        part.center_adjust.y,
        part.size.z/2 - plate_size.z + part.center_adjust.z
    ]) {
        import(part.file, center=true);
    }
}
