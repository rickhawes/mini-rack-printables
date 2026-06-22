//------------------------------------------------------------------------------------------------
// Geometry
//
// Helpful structures and functions for rectangles and their padding
//
//------------------------------------------------------------------------------------------------
include <BOSL2/std.scad>;


//
// rects are vectors with x,y,dx,dy tuples
//
function build_rect(x, y, dx, dy) =
    assert(dx >= 0 && dy >= 0)
    [x, y, dx, dy];

function build_rect_with_offset(dx, dy, offset_x=0, offset_y=0) =
    build_rect(-dx/2 + offset_x, -dy/2 + offset_y, dx, dy);

function rect_from_edges(right, left, top, bottom) =
    build_rect(left, bottom, right-left, top-bottom);

function is_rect(rect) =
    is_list(rect) && len(rect) == 4 && is_num(rect[0]);

function rect_x(rect) = 
    assert(is_rect(rect))
    rect[0];

function rect_y(rect) = 
    assert(is_rect(rect))
    rect[1];

function rect_dx(rect) = 
    assert(is_rect(rect))
    rect[2];

function rect_dy(rect) =
    assert(is_rect(rect))
    rect[3];    

function rect_left(rect) = 
    rect_x(rect);

function rect_bottom(rect) = 
    rect_y(rect);

function rect_right(rect) = 
    rect_x(rect) + rect_dx(rect);

function rect_top(rect) =
    rect_y(rect) + rect_dy(rect);

function rect_offset_x(rect) = 
    rect_x(rect) + rect_dx(rect)/2;

function rect_offset_y(rect) = 
    rect_y(rect) + rect_dy(rect)/2;

function rect_offset(rect) = 
    [rect_offset_x(rect), rect_offset_y(rect)];

//
// A margin has multiple forms
// - An constant outset
// - Different x and y outset 
// - Different right, left, top, bottom
//
function build_margin(margin,dx,dy,right,left,top,bottom) = 
    let (
        x_right = !is_undef(right) ? right : !is_undef(dx) ? dx : !is_undef(margin) ? margin : 0,
        x_left = !is_undef(left) ? left : !is_undef(dx) ? dx : !is_undef(margin) ? margin : 0, 
        y_top = !is_undef(top) ? top : !is_undef(dy) ? dy : !is_undef(margin) ? margin : 0, 
        y_bottom = !is_undef(bottom) ? bottom : !is_undef(dy) ? dy : !is_undef(margin) ? margin : 0
    )
    [x_right, x_left, y_top, y_bottom];

function is_margin(margin) =
    is_num(margin) ||
    is_list(margin) && len(margin) == 2 && is_num(margin[0]) && is_num(margin[1]) ||
    is_list(margin) && len(margin) == 4 && is_num(margin[0]) && is_homogeneous(margin);

function normalize_margin(margin) =
    assert(is_margin(margin))
    is_num(margin) ? [margin, margin, margin, margin] :
    is_list(margin) && len(margin) == 2 ? [margin[0], margin[1], margin[0], margin[1]] :
    margin;

function union_margin(margin1, margin2) =
    let (
        norm1 = normalize_margin(margin1),
        norm2 = normalize_margin(margin2)
    )
    [
        max(norm1[0], norm2[0]), 
        max(norm1[1], norm2[1]), 
        max(norm1[2], norm2[2]), 
        max(norm1[3], norm2[3])         
    ];

function apply_margin(rect, margin) =
    let(b = normalize_margin(margin))
    rect_from_edges(
        right = rect_right(rect) + b[0], 
        left = rect_left(rect) - b[1], 
        top = rect_top(rect) + b[2],
        bottom = rect_bottom(rect) - b[3] 
    );


// Grow a rectangle in opposite direction of the offset by the amount needed to 
// to center a rect. 
function grow_to_center(rc) = 
    assert(is_rect(rc))
    let(
        offset_x = rect_offset_x(rc),
        offset_y = rect_offset_y(rc),
        left = offset_x >= 0 ? rect_left(rc) - 2*offset_x : rect_left(rc),
        right = offset_x >= 0 ? rect_right(rc) : rect_right(rc) - 2*offset_x, 
        bottom = offset_y >= 0 ? rect_bottom(rc) - 2*offset_y : rect_bottom(rc),
        top = offset_y >= 0 ? rect_top(rc) : rect_top(rc) - 2*offset_y 
    )
    rect_from_edges(right,left,top,bottom);

