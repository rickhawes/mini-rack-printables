from mini_rack_printables import Faceplate, JetKVM

#
# This example demonstrates a faceplate with a Jet KVM cutout.
#
plate = Faceplate(rack_units=1.5, features=[[JetKVM()]]).render()

# Show the plate in the OCP viewer
plate.show()

# Export the plate as a STEP file as well
plate.export_step("outputs/face_plate_with_jetkvm.step")
