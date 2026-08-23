import build123d as bd
from ocp_vscode import show

from mini_rack_printables import FacePlate

#
# This example demonstrates a blank face plate with a rib.
#

plate = FacePlate(rack_units=1.0, rib_size=FacePlate.STD_RIB).render()

# Show the plate in the viewer. Run 'task viewer' before.
show(plate)

# Export the plate to a STEP file
bd.export_step(plate, "outputs/blank_face_plate.step")
