from mini_rack_printables import Faceplate, Vec3, WallHolder

#
# This example demonstrates a faceplate with a holder.
#
holder = WallHolder(device_size=Vec3(210.0, 33.1, 30), style=WallHolder.BACK_LIP)
plate = Faceplate(rack_units=1.0, features=[[holder]]).render()

# Show the plate in the OCP viewer
plate.show()

# Export the plate as a STEP file as well
plate.export_step("outputs/face_plate_with_holder.step")
