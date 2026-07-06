//------------------------------------------------------------------------------------------------
// Geometry
//
// Helpful structures and functions for rectangles and their padding
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;


//
// RC are structures representing a rectangle in the x-y plane. 
// They contain a size vector [dx, dy] and a shift vector [x, y].
// They have nice arithmetical attributes for layout, with a centered rectangle being the default. 
//
RC_SIZE = "size";
RC_SHIFT = "shift";

function rc(size, shift=[0,0]) =
    assert(size.x >= 0 && size.y >= 0)
    struct_set([], [RC_SIZE, size, RC_SHIFT, shift]);

function rc_from_edges(right, left, top, bottom) =
    rc(size = [right-left, top-bottom], shift = [(right+left)/2, (top+bottom)/2]);

function is_rc(r) =
    let(keys = struct_keys(r))
    is_struct(r) && in_list(RC_SIZE, keys) && in_list(RC_SHIFT, keys);

function rc_size(r) = 
    struct_val(r, RC_SIZE);

function rc_shift(r) = 
    struct_val(r, RC_SHIFT);

function rc_left(r) = 
    -rc_size(r).x/2 + rc_shift(r).x;

function rc_bottom(r) = 
    -rc_size(r).y/2 + rc_shift(r).y;

function rc_right(r) = 
    rc_left(r) + rc_size(r).x;

function rc_top(r) =
    rc_bottom(r) + rc_size(r).y;

function rc_union(r1, r2) = 
    assert(is_rc(r1) && is_rc(r2))
    rc_from_edges(
        right = max(rc_right(r1), rc_right(r2)),
        left = min(rc_left(r1), rc_left(r2)),
        top = max(rc_top(r1), rc_top(r2)),
        bottom = min(rc_bottom(r1), rc_bottom(r2))
    );



// 
// CU are structures representing a cuboid in the 3d space. 
// They contain a size vector [dx, dy, dz] and a shift vector [x, y, z].
// They have nice arithmetical attributes for layout, with a centered cuboid being the default. 
// 

CU_SIZE = "cu_size";
CU_SHIFT = "cu_shift";

function cu(size, shift=[0,0,0]) = 
    assert(size.x >= 0 && size.y >= 0 && size.z >= 0)
    struct_set([], [CU_SIZE, size, CU_SHIFT, shift]);

function is_cu(c) =
    let(keys = struct_keys(c))
    is_struct(c) && in_list(CU_SIZE, keys) && in_list(CU_SHIFT, keys);


function cu_shift(c) = 
    struct_val(c, CU_SHIFT);

function cu_size(c) =
    struct_val(c, CU_SIZE);

function rc_from_cu(c) =
    rc(size = [cu_size(c).x, cu_size(c).y], shift = [cu_shift(c).x, cu_shift(c).y]);

function cu_from_rc(r, z=0, dz=0) = 
    cu(size = [rc_size(r).x, rc_size(r).y, dz], shift = [rc_shift(r).x, rc_shift(r).y, z]);

//
// A padding has multiple forms
// - An constant outset
// - Different x and y outset 
// - Different right, left, top, bottom
//
function build_padding(padding,dx,dy,right,left,top,bottom) = 
    let (
        x_right = !is_undef(right) ? right : !is_undef(dx) ? dx : !is_undef(padding) ? padding : 0,
        x_left = !is_undef(left) ? left : !is_undef(dx) ? dx : !is_undef(padding) ? padding : 0, 
        y_top = !is_undef(top) ? top : !is_undef(dy) ? dy : !is_undef(padding) ? padding : 0, 
        y_bottom = !is_undef(bottom) ? bottom : !is_undef(dy) ? dy : !is_undef(padding) ? padding : 0
    )
    [x_right, x_left, y_top, y_bottom];

function is_padding(padding) =
    is_num(padding) ||
    is_list(padding) && len(padding) == 2 && is_num(padding[0]) && is_num(padding[1]) ||
    is_list(padding) && len(padding) == 4 && is_num(padding[0]) && is_homogeneous(padding);

function normalize_padding(padding) =
    assert(is_padding(padding))
    is_num(padding) ? [padding, padding, padding, padding] :
    is_list(padding) && len(padding) == 2 ? [padding[0], padding[1], padding[0], padding[1]] :
    padding;

function union_padding(padding1, padding2) =
    let (
        norm1 = normalize_padding(padding1),
        norm2 = normalize_padding(padding2)
    )
    [
        max(norm1[0], norm2[0]), 
        max(norm1[1], norm2[1]), 
        max(norm1[2], norm2[2]), 
        max(norm1[3], norm2[3])         
    ];


//
// RC functions for layout
//

function rc_divided_horizontally(r, by) = 
    let(
        division_dx = rc_size(r).x/by,
        even = by % 2 == 0,
        end = even ? floor(by/2) - 0.5 : floor(by/2),
        start = -end

    )[
        for(i = [start:1.0:end])
            rc([division_dx, rc_size(r).y], [rc_shift(r).x + i*division_dx, rc_shift(r).y])
    ];

function rc_divided_vertically(r, by) = 
    let(
        division_dy = rc_size(r).y/by,
        even = by % 2 == 0,
        end = even ? floor(by/2) - 0.5 : floor(by/2),
        start = -end

    )[
        for(i = [start:1.0:end])
            rc([rc_size(r).x, division_dy], [rc_shift(r).x, rc_shift(r).y + i*division_dy])
    ];

// Apply padding to a rectangle. Given a rectangle and a padding, return a new rectangle with the padding applied.
function apply_padding(r, padding) =
    assert(is_rc(r) && is_padding(padding))
    let(b = normalize_padding(padding))
    rc_from_edges(
        right   = rc_right(r)   + b[0], 
        left    = rc_left(r)    - b[1], 
        top     = rc_top(r)     + b[2],
        bottom  = rc_bottom(r)  - b[3] 
    );

// Shift by alignment. Given a bounding rectangle, another rectangle's size and an alignment, return a shift amount to align.
function alignment_shift(bounding_rc, align, size) =
    [
        (rc_size(bounding_rc).x - size.x)*align.x/2 + rc_shift(bounding_rc).x,
        (rc_size(bounding_rc).y - size.y)*align.y/2 + rc_shift(bounding_rc).y
    ];

// Grow a rectangle in opposite direction of the offset by the amount needed to 
// to center a rect. 
function centered_bounding_rc(r) = 
    assert(is_rc(r))
    let(
        shift = rc_shift(r),
        rc_mirror = rc(size = rc_size(r), shift = [-shift.x, -shift.y]),
    )
    rc_union(r, rc_mirror);
