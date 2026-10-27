from mini_rack_printables import CornerHolder, FeatureXRayModel, RectangleElement

#
# This example demonstrates a corner holder part.
#
holder = CornerHolder(RectangleElement(100, 100, 5), corner_width=12, corner_height=12)
plate = FeatureXRayModel(holder, only_adds=False).render()

# Show the plate in the OCP viewer
plate.show()
