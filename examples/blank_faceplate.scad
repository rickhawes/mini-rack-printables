include <../main.scad>
$fn = 20;

fp = face_plate(
    rack_units = 1.0,
    faceplate_thickness = 3.5,
    middle_holes = true,
    bottom_is_half_height = false,
    rib_size = [2.0, 1.0]
);

render_assembly(fp);
