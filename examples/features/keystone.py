from ocp_vscode import show
from mini_rack_printables import XRayModel, Keystone

#
# This example demonstrates a keystone cutout.
#
plate = XRayModel(Keystone()).render()

# Show the plate in the OCP viewer
show(plate)
