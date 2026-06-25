
//------------------------------------------------------------------------------------------------
// Shapes 
//
// Modules to draw useful 2d & 3d shapes
// Modules to draw common 2d & 3d shapes
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

// Made with achnor points and attablable
module extruded_roundrect(size, r, anchor) {
    cuboid(size, rounding=r, edges=[FRONT+LEFT,FRONT+RIGHT,BACK+RIGHT,BACK+LEFT], anchor=anchor) {
        children();
    }
}

// Extrude a rib based on the 2d shape of the children
module extrude_rib(rib_size) {
    linear_extrude(height=rib_size.y) 
        difference() {
            offset(delta=rib_size.x) 
                children();
            children();
        }
}

// Made with achnor points and attablable
module extruded_roundrect(size, r, anchor) {
    cuboid(size, rounding=r, edges=[FRONT+LEFT,FRONT+RIGHT,BACK+RIGHT,BACK+LEFT], anchor=anchor) {
        children();
    }
}