from ocp_vscode import show
from mini_rack_printables import XRayModel, PuckHolder

#
# This example demonstrates a corner holder part.
#
holder = PuckHolder(device_size=(100, 40, 100), device_rounding=10)
plate = XRayModel(holder, only_adds=False).render()

# Show the plate in the OCP viewer
show(plate)
