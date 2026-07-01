//------------------------------------------------------------------------------------------------
// Division
//
// A div is used to layout a section of a plate by evenly dividing the plate in either 
// the horizontal (default) or verticle direction. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>
include <base.scad>
include <geometry.scad>

//------------------------------------------------
// Part Constants
//------------------------------------------------
/* [Hidden] */

// Vertical direction
VERTICAL = "vertical";

// Horizontal direction
HORIZONTAL = "horizontal";

// value for the type of a part
DIV_TYPE        = "div";
DIV_PARTS       = "parts";
DIV_DIR         = "dir";

//------------------------------------------------
// Functions
//------------------------------------------------


function div(
    dir = HORIZONTAL, 
    align=CENTER, 
    padding = 0, 
    shift = [0,0],
    parts = []
) = struct_set(
    part_base(DIV_TYPE, align, padding, shift), [
        DIV_DIR, dir,
        DIV_PARTS, parts
    ]);

function is_div(part) =
    is_struct(part) && get_subtype(part) == DIV_TYPE;

function div_parts(part) =
    struct_val(part, DIV_PARTS);

function div_dir(part) =
    struct_val(part, DIV_DIR);


// Take a section and divide it into even sections. Return the results as cubiods. 
function divide_horizontally(section_size, by) = 
    let(section_rc = rc(size = [section_size.x, section_size.y]))
    rc_divided_horizontally(r = section_rc, by = by);
    
// 
function layout_parts(parts, section_size) = 
    let(
        num = len(parts),
        half_num = floor(num/2),
        mid_part = num % 2 == 0 ? undef: [parts[half_num]],
        dx_section = section_size.x/num,
        mid_dx = is_undef(mid_part) ? 0 : dx_section
    )
    concat(
        [for(i=[-half_num+1:1:0]) [-mid_dx/2 - dx_section/2 + i*dx_section, 0]],
        is_undef(mid_part) ? [] : [[0,0]],
        [for(i=[0:1:half_num-1]) [mid_dx/2 + dx_section/2 + i*dx_section, 0]]
    );

module _render_div(part, section_size) {
    dir = div_dir(part);
    sub_parts = div_parts(part);
    sub_sections = divide_horizontally(section_size, by=len(sub_parts));
    layout_pts = layout_parts(sub_parts, section_size);

    for(i = [0:1:len(sub_parts)-1]) {
        sub_size = [rc_size(sub_sections[i]).x, rc_size(sub_sections[i]).y, section_size.z];
        translate(layout_pts[i]) {
            render_part(sub_parts[i], sub_size);
        }
    }    
}
