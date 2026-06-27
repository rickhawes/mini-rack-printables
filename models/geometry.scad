//------------------------------------------------------------------------------------------------
// Geometry
//
// Helpful structures and functions for rectangles and their padding
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;


//
// rc are vectors representing a rectangle. They are vectors with [x,y,dx,dy] values.
//
function rc(x=0, y=0, dx=0, dy=0) =
    assert(dx >= 0 && dy >= 0)
    [x, y, dx, dy];

function centered_rc(dx, dy) =
    assert(dx >= 0 && dy >= 0)
    [-dx/2, -dy/2, dx, dy];

function shifted_rc(dx, dy, shift_x=0, shift_y=0) =
    rc(-dx/2 + shift_x, -dy/2 + shift_y, dx, dy);

function rc_from_edges(right, left, top, bottom) =
    rc(left, bottom, right-left, top-bottom);

function is_rc(r) =
    is_list(r) && len(r) == 4 && is_num(r[0]);

function rc_x(r) = 
    assert(is_rc(r))
    r[0];

function rc_y(r) = 
    assert(is_rc(r))
    r[1];

function rc_dx(r) = 
    assert(is_rc(r))
    r[2];

function rc_dy(r) =
    assert(is_rc(r))
    r[3];    

function rc_left(r) = 
    rc_x(r);

function rc_bottom(r) = 
    rc_y(r);

function rc_right(r) = 
    rc_x(r) + rc_dx(r);

function rc_top(r) =
    rc_y(r) + rc_dy(r);

function rc_shift(r) = 
    [rc_x(r) + rc_dx(r)/2, rc_y(r) + rc_dy(r)/2];

function rc_size(r) =
    [rc_dx(r), rc_dy(r)];

function rc_from_size(s) =
    centered_rc(s.x, s.y);

function rc_divided_horizontally(r, by) = 
    let(
        dx = rc_dx(r), 
        sub_section_dx = dx/by
    )[
        for(i = [0:1:by-1])
            let(x = rc_x(r) + i*sub_section_dx)
            rc(x, y=rc_y(r), dx=sub_section_dx, dy=rc_dy(r))
    ];

// 
// Cubiods are sometimes called rectangular parallelpideds or rectangular cubiods in analytical geometry.
// They have 3 pairs of rectangles as faces. They defined by an [x, y, z, dx, dy, dz] vector. 
// 

function cu(x=0, y=0, z=0, dx=0, dy=0, dz=0) = 
    assert(dx >= 0 && dy >= 0 && dz >= 0)
    [x, y, z, dx, dy, dz];

function centered_cu(dx, dy, dz) =
    cu(-dx/2, -dy/2, -dz/2, dx, dy, dz);

function shifted_cu(dx, dy, dz, shift_x=0, shift_y=0, shift_z=0) = 
    cu(-dx/2 + shift_x, -dy/2 + shift_y, -dz/2 + shift_z, dx, dy, dz);

function is_cu(c) =
    is_list(c) && len(c) == 6 && is_num(c[0]);

function cu_x(c) = 
    assert(is_cu(c))
    c[0];

function cu_y(c) = 
    assert(is_cu(c))
    c[1];

function cu_z(c) = 
    assert(is_cu(c))
    c[2];

function cu_dx(c) = 
    assert(is_cu(c))
    c[3];

function cu_dy(c) =
    assert(is_cu(c))
    c[4];    

function cu_dz(c) =
    assert(is_cu(c))
    c[5];   

function cu_from_rc(r, z=0, dz=0) = 
    cu(rc_x(r), rc_y(r), z, rc_dx(r), rc_dy(r), dz);

function cu_center(c) = 
    [cu_x(c) + cu_dx(c)/2, cu_y(c) + cu_dy(c)/2, cu_z(c) + cu_dz(c)/2];

function cu_size(c) =
    [cu_dx(c), cu_dy(c), cu_dz(c)];

function cu_from_size(s) =
    centered_cu(s.x, s.y, s.z);

function rc_from_cu(c) =
    rc(cu_x(c), cu_y(c), cu_dx(c), cu_dy(c));


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

function apply_padding(r, padding) =
    let(b = normalize_padding(padding))
    rc_from_edges(
        right = rc_right(r) + b[0], 
        left = rc_left(r) - b[1], 
        top = rc_top(r) + b[2],
        bottom = rc_bottom(r) - b[3] 
    );


// Grow a rectangle in opposite direction of the offset by the amount needed to 
// to center a rect. 
function grow_to_center(r) = 
    assert(is_rc(r))
    let(
        shift = rc_shift(r),
        left    = shift.x >= 0 ? rc_left(r) - 2*shift.x     : rc_left(r),
        right   = shift.x >= 0 ? rc_right(r)                : rc_right(r) - 2*shift.x, 
        bottom  = shift.y >= 0 ? rc_bottom(r) - 2*shift.y   : rc_bottom(r),
        top     = shift.y >= 0 ? rc_top(r)                  : rc_top(r) - 2*shift.y 
    )
    rc_from_edges(right,left,top,bottom);

