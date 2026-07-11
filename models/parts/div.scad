//------------------------------------------------------------------------------------------------
// Division
//
// A div is used to layout a section of a plate by evenly dividing the plate in either 
// the horizontal (default) or verticle direction. 
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>
include <../geometry.scad>
include <part_base.scad>


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
DIV_SIZES       = "sizes";

// A section is an internal struct representing a particular section of a plate. 
SECTION_PART   = "section_part";
SECTION_SIZE   = "section_size";
SECTION_SHIFT  = "section_shift";

//------------------------------------------------
// Div Structure
//------------------------------------------------

// Create a div part
function div(
    dir = HORIZONTAL, 
    align = CENTER, 
    padding = 0, 
    shift = [0,0],
    sizes = ["*"],
    parts = []
) = 
    assert(len(sizes) <= len(parts), "Must have less sizes than parts")
    struct_set(
        part_base(
            DIV_TYPE, 
            align, 
            padding, 
            shift
        ), [
        DIV_DIR, dir,
        DIV_PARTS, parts,
        DIV_SIZES, sizes
    ]);

function is_div(part)       = is_struct(part) && part_type(part) == DIV_TYPE;
function div_parts(part)    = struct_val(part, DIV_PARTS);
function div_dir(part)      = struct_val(part, DIV_DIR);
function div_sizes(part)    = struct_val(part, DIV_SIZES);


//------------------------------------------------
// Layout functions
//------------------------------------------------

function count_auto(vec, i = 0, c = 0) = 
    i < len(vec) ? 
        count_auto(vec, i+1, c + (vec[i] == "*" ? 1 : 0)) :
        c;

function sum_static(vec, i = 0, s = 0) =
    i < len(vec) ? 
        sum_static(vec, i+1, s + (vec[i] == "*" ? 0 : vec[i])) :
        s;

function is_sizes_valid(sizes) = 
    assert(is_list(sizes))
    let(
        tests = [
            for (
                valid = true, i=0; 
                i <= len(sizes); 
                valid = valid && ((is_num(sizes[i]) && sizes[i] > 0) || sizes[i] == "*"), i = i+1
            ) 
            valid
        ]
    )
    tests[len(sizes)];

// Extend the size array to match the parts (i.e. one size for each part)
function extend_sizes(sizes, num_parts) =
    let (
        last_size = sizes[len(sizes)-1],
        sizes_needed = num_parts - len(sizes) 
    )
    sizes_needed > 0 ?
        concat(sizes, repeat(last_size, sizes_needed)) :
        sizes;

// Replace sizes with "*" with the auto size
function fill_in_auto_sizes(r, sizes, dir=HORIZONTAL) =
    assert(is_sizes_valid(sizes))
    let(
        r_size = dir == HORIZONTAL ? rc_size(r).x : rc_size(r).y,
        num_auto = count_auto(sizes),
        total_auto_size = r_size - sum_static(sizes),
    )
    assert(total_auto_size >= 0, "static sizes must be less than the r size")
    num_auto == 0 ? 
        sizes :
        let(auto_size = total_auto_size / num_auto)
        [for(size = sizes) size == "*" ? auto_size: size];

// Divide recursizely based on sizes without "*" auto sizes
function divide_recursive(r, sizes, dir) = 
    len(sizes) == 1 ? 
        [r] :
        let(
            size = sizes[0],
            r_split = dir == HORIZONTAL ? rc_split(r, dx=size) : rc_split(r, dy=size)
        )
        concat(
            [r_split[0]],
            divide_recursive(r_split[1], slice(sizes, 1, -1), dir)
        );

// Divide a RC based on sizes with auto parameters
function divide_rc(r, sizes, dir=HORIZONTAL) = 
    let(adjusted_sizes = fill_in_auto_sizes(r, sizes, dir))
    divide_recursive(r, adjusted_sizes, dir);

// Divide the plate based on parts and their align and shift properties
function divide_plate(sub_parts, plate_size, section_sizes=["*"], dir=HORIZONTAL) = 
    let(
        num_parts = len(sub_parts),
        extended_sizes = extend_sizes(sizes = section_sizes, num_parts = num_parts),
        sub_sections_rc = divide_rc(rc(plate_size), extended_sizes, dir)
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
            SECTION_PART, sub_part,
            SECTION_SIZE, [rc_size(sub_section_rc).x, rc_size(sub_section_rc).y, plate_size.z],
            SECTION_SHIFT, shift
        ])
    ];

function section_part(section)    = struct_val(section, SECTION_PART);
function section_size(section)    = struct_val(section, SECTION_SIZE);
function section_shift(section)   = struct_val(section, SECTION_SHIFT);


//------------------------------------------------
// Rendering functions
//------------------------------------------------


module _render_div(part, plate_size) {
    sections = divide_plate(
        div_parts(part), 
        plate_size,
        section_sizes=div_sizes(part),
        dir=div_dir(part)
    );
    for(section = sections) {
        translate(section_shift(section)) {
            render_part(section_part(section), section_size(section));
        }
    }
}
