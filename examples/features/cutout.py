from ocp_vscode import show

from mini_rack_printables import Cutout, Faceplate, SlotElement, XRayModel

#
# This example demonstrates a corner holder part.
#
part = Cutout(SlotElement(10.0, 5.0), rib=Faceplate.STD_RIB)
plate = XRayModel(part, only_adds=False).render()

# Show the plate in the OCP viewer
show(plate)
