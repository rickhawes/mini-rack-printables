from mini_rack_printables import Keystone, XRayModel

#
# This example demonstrates a keystone cutout.
#
plate = XRayModel(Keystone()).render()

# Show the plate in the OCP viewer
plate.show()
