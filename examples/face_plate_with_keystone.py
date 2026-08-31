import build123d as bd
from ocp_vscode import show

from mini_rack_printables import Keystone, Div, FacePlate

#
# This example demonstrates a face plate with a keystone cutout.
#

# A basic Div with horizontal layout and evenly divided sections for 3 keystones
keystone_part = Keystone()
div = Div(parts=[keystone_part for _ in range(3)])
plate = FacePlate(
    rack_units=1.0,
    rib=FacePlate.STD_RIB,
    part=div,
).render()

# Show the plate in the OCP viewer
show(plate)

# Export the plate as a STEP file as well
bd.export_step(plate, "outputs/face_plate_with_keystone.step")
