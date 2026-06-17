include <../main.scad>
$fn = 20;

// Common rib size 
rib_size = [2.0, 1.0];

part = rect_cutout(
    size = [10,10],
    rounding = 2.0, 
    name = "keyhole", 
    rib_size = rib_size
);

faceplate(
    rack_units = 1.0,
    faceplate_thickness = 3.5,
    middle_holes = true,
    bottom_is_half_height = false,
    rib_size = rib_size,
    part
);

