include <../main.scad>

$fn = 20;

// Common rib size 
rib_size = [2.0, 1.0];

part = keystone();

fp = face_plate(
    rack_units = 1.0,
    thickness = 3.5,
    middle_holes = true,
    half_alignment = false,
    rib_size = rib_size,
    part
);

render_assembly(assembly = fp);