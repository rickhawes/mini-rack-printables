
//------------------------------------------------------------------------------------------------
// Shapes 
//
// Modules to draw common 2d shapes
//
//------------------------------------------------------------------------------------------------

// Made by joining two circles in the x direction
module slot_xaxis(dx, r) {
    hull() {
        d = max((dx/2) - r, 0);
        translate([d, 0])
            circle(r=r);
        translate([-d, 0])
            circle(r=r);
    }    
}

// Made by joining two circles in the y-direction
module slot_yaxis(dy, r) {
    hull() {
        d = max((dy/2) - r, 0);
        translate([0, d])
            circle(r=r);
        translate([0, -d])
            circle(r=r);
    }    
}