include <../main.scad>
$fn = 20;

fp = face_plate(
	track_units = 1.0,
	thickness = 3.5,
	middle_holes = true,
	half_alignment = false,
	rib_size = [2.0, 1.0]
);

render_assembly(fp);
