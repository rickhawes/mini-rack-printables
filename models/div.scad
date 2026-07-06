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

// A divisions is struct representing a division of a plate into multiple sections. 
DIVISION_PART   = "division_part";
DIVISION_SIZE   = "division_size";
DIVISION_SHIFT  = "division_shift";

//------------------------------------------------
// Functions
//------------------------------------------------


function div(
    dir = HORIZONTAL, 
    align = CENTER, 
    padding = 0, 
    shift = [0,0],
    parts = []
) = struct_set(
        part_base(
            DIV_TYPE, 
            align, 
            padding, 
            shift
        ), [
        DIV_DIR, dir,
        DIV_PARTS, parts
    ]);

function is_div(part)       = is_struct(part) && get_subtype(part) == DIV_TYPE;
function div_parts(part)    = struct_val(part, DIV_PARTS);
function div_dir(part)      = struct_val(part, DIV_DIR);


function divide_section(sub_parts, section_size, dir = HORIZONTAL) = 
    let(
        num_parts = len(sub_parts),
        sub_sections_rc = dir == HORIZONTAL ? 
            rc_divided_horizontally(rc(section_size), by = num_parts) : 
            rc_divided_vertically(rc(section_size), by = num_parts)
    )
    [for(i = [0:1:num_parts-1]) 
        let(
            sub_part = sub_parts[i],
            sub_section_rc = sub_sections_rc[i],
            layout_size = part_layout_size(sub_part),
            layout_with_padding = apply_padding(rc(layout_size), part_padding(sub_part)),
            shift = alignment_shift(
                bounding_rc = sub_section_rc, 
                align = part_align(sub_part), 
                size = rc_size(layout_with_padding)
            ) + part_shift(sub_part)
        )
        struct_set([], [
            DIVISION_PART, sub_part,
            DIVISION_SIZE, [rc_size(sub_section_rc).x, rc_size(sub_section_rc).y, section_size.z],
            DIVISION_SHIFT, shift
        ])
    ];

function division_part(division)    = struct_val(division, DIVISION_PART);
function division_size(division)    = struct_val(division, DIVISION_SIZE);
function division_shift(division)   = struct_val(division, DIVISION_SHIFT);

module _render_div(part, section_size) {
    divisions = divide_section(div_parts(part), section_size, div_dir(part));
    for(division = divisions) {
        translate(division_shift(division)) {
            render_part(division_part(division), division_size(division));
        }
    }
}
