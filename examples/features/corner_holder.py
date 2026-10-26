from mini_rack_printables import CornerHolder, RectangleElement, XRayModel

#
# This example demonstrates a corner holder part.
#
holder = CornerHolder(RectangleElement(100, 100, 5), corner_width=12, corner_height=12)
plate = XRayModel(holder, only_adds=False).render()

# Show the plate in the OCP viewer
plate.show()
