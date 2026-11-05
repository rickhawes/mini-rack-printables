"""This example demonstrates a 10-inch rack faceplate with a 3 network
keystone cutouts."""

from mini_rack_printables import FaceplateStyle, Keystone, faceplate

# A 1u faceplace with ribs and one row with 3 network keystone cutouts.
plate = faceplate(
    rack_units=1.0,
    style=FaceplateStyle(rib=FaceplateStyle.STD_RIB),
    features=[[Keystone()] * 3],
)

# Show the plate in the OCP viewer
plate.show()

# Export the plate as a STEP file as well
plate.export_step("outputs/faceplate_with_keystone.step")
