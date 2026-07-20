include <../main.scad>

$fn = 20;


// Create a holder
part = div(
    parts = [
        holder(STYLE_BACK_LIP, device_size=[212.8, 33.1, 10], wall_rounding = 1.5)
    ]
);

fp = face_plate(
    rack_units = 1.0,
    thickness = 3.5,
    middle_holes = true,
    half_alignment = false,
    part = part
);

render_assembly(assembly = fp);
