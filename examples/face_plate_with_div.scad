include <../main.scad>
$fn = 20;

// Common rib size 
rib_size = [2.0, 1.0];

partTop = rect_cutout(
    size = [10,10],
    rounding = 2.0,
    align = BACK,
    padding = 1.0,
    rib_size = rib_size
);

partCenter = rect_cutout(
    size = [10,10],
    rounding = 2.0,
    align = CENTER
);

partBottom = rect_cutout(
    size = [10,10],
    rounding = 2.0,
    align = FRONT,
    rib_size = rib_size
);

div = div(
    parts = [partTop, partCenter, partBottom]
);

fp = face_plate(
    rack_units = 1.0,
    thickness = 3.5,
    middle_holes = true,
    half_alignment = false,
    rib_size = rib_size,
    part = div
);

render_assembly(assembly = fp);
