from mini_rack_printables import BoxHolder, FeatureXRayModel, Vec3

#
# This example demonstrates a keystone cutout.
#
holder = BoxHolder(device_size=Vec3(60, 30, 40), device_rounding=1.0, style=BoxHolder.BACK_LIP)
plate = FeatureXRayModel(holder, only_adds=False).render()

# Show the plate in the OCP viewer
plate.show()
