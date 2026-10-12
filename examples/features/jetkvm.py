from ocp_vscode import show
from mini_rack_printables import XRayModel, JetKVM

#
# This example demonstrates a Jet KVM cutout.
#
plate = XRayModel(JetKVM(), only_adds=False).render()

# Show the plate in the OCP viewer
show(plate)
