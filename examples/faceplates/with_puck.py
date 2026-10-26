from mini_rack_printables import Faceplate, PuckHolder, Vec3

#
# This example demonstrates a faceplate with a puck holder.
#
holder = PuckHolder(
    device_size=Vec3(60, 30, 60), device_rounding=10, style=PuckHolder.Style(has_cutout=True)
)
plate = Faceplate(rack_units=1.0, features=[[holder]]).render()

# Show the plate in the OCP viewer
plate.show()

# Export the plate as a STEP file as well
plate.export_step("outputs/face_plate_with_puck.step")
