from ocp_vscode import show
from mini_rack_printables import XRayModel, WallHolder


#
# This example demonstrates a keystone cutout.
#
holder = WallHolder(device_size=(60, 30, 40), device_rounding=1.0, style=WallHolder.NO_CUTOUT)
plate = XRayModel(holder, only_adds=False).render()

# Show the plate in the OCP viewer
show(plate)
