from mini_rack_printables import FacePlate

fp = FacePlate(
    rack_units = 1.0,
	thickness = 3.5,
	middle_holes = True,
	half_alignment = False,
	rib_size = [2.0, 1.0]
)

fp.render().save_as_scad("output/blank_face_plate.scad")