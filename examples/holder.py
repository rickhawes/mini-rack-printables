from ocp_vscode import show
from mini_rack_printables import XRayModel, Holder, HolderStyle
from build123d import Vector


#
# This example demonstrates a keystone cutout.
#
holder = Holder(style=HolderStyle.FRONT_LIP, device_size=Vector(60, 30, 40), device_rounding=1.0)
plate = XRayModel(holder, only_adds=False).render()

# Show the plate in the OCP viewer
show(plate)

