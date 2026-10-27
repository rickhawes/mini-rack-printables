from mini_rack_printables import FeatureXRayModel, JetKVM

#
# This example demonstrates a Jet KVM cutout.
#
plate = FeatureXRayModel(JetKVM(), only_adds=True).render()

# Show the plate in the OCP viewer
plate.show()
