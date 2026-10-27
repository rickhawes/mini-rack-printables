from mini_rack_printables import Cutout, Faceplate, FeatureXRayModel, SlotElement

#
# This example demonstrates a corner holder part.
#
feature = Cutout(SlotElement(10.0, 5.0), rib=Faceplate.STD_RIB)
plate = FeatureXRayModel(feature, only_adds=False).render()

# Show the plate in the OCP viewer
plate.show()
