from mini_rack_printables import Faceplate

#
# This example demonstrates a blank faceplate with a rib.
#

plate = Faceplate(rack_units=1.0).render()

# Show the plate in the viewer. Run 'task viewer' before.
plate.show()

# Export the plate to a STEP file
plate.export_step("outputs/blank_face_plate.step")
