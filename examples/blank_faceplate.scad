include <../main.scad>
$fn = 20;

fp = face_plate(
part = rect_cutout([-5,-5,10,10]);

faceplate(
    rack_units = 1.0,
    faceplate_thickness = 3.5,
    middle_holes = true,
    bottom_is_half_height = false,
    rib_size = [2.0, 1.0]
    add_ribs = true,
    part
);

render_assembly(fp);
