"""This example shows a Keystone feature."""

from mini_rack_printables import Keystone, XRayShow, feature_xray

#
# This example demonstrates a keystone cutout.
#
model = feature_xray(Keystone(), show=XRayShow.ALL)

# Show the model in the OCP viewer
model.show()
