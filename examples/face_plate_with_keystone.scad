include <../main.scad>

$fn = 20;

// Common rib size 
rib_size = [2.0, 1.0];


// Create an area with 5 identical keystones
part = div(
    parts = repeat(keystone(), 5)
);

fp = face_plate(
    rack_units = 1.0,
    thickness = 3.5,
    middle_holes = true,
    half_alignment = false,
    rib_size = rib_size,
    part
);

render_assembly(assembly = fp);