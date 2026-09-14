import build123d as bd
from ocp_vscode import show

from mini_rack_printables import PuckHolder, FacePlate, Div, PuckHolderStyle

#
# This example demonstrates a face plate with a puck holder.
#
holder = PuckHolder(
    device_size=(60, 30, 60), device_rounding=10, style=PuckHolderStyle(has_cutout=True)
)
plate = FacePlate(rack_units=1.0, part=Div(parts=[holder])).render()

# Show the plate in the OCP viewer
show(plate)

# Export the plate as a STEP file as well
bd.export_step(plate, "outputs/face_plate_with_puck.step")
