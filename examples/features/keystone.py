from mini_rack_printables import FeatureXRayModel, Keystone

#
# This example demonstrates a keystone cutout.
#
plate = FeatureXRayModel(Keystone(), only_adds=False).render()

# Show the plate in the OCP viewer
plate.show()
