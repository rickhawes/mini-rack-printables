// Made by joining two circles in the x direction
module slot_2d(dx, r) {
    hull() {
        d = max((dx/2) - r, 0);
        translate([d, 0])
            circle(r=r);
        translate([-d, 0])
            circle(r=r);
    }    
}