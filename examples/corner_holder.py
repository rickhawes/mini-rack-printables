from ocp_vscode import show
from mini_rack_printables import XRayModel, CornerHolder, RectangleElement

#
# This example demonstrates a corner holder part.
#
holder = CornerHolder(RectangleElement(100, 100, radius=5), corner_width=12, corner_height=12)
plate = XRayModel(holder, only_adds=False).render()

# Show the plate in the OCP viewer
show(plate)
