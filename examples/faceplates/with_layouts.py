from mini_rack_printables import (
    CircleElement,
    Cutout,
    Dir2,
    Faceplate,
    RectangleElement,
    RowLayout,
    SlotElement,
)

#
# This example demonstrates a faceplate with a RowLayout containing 3 cutouts.
# Each cutout has a different alignment and padding and shift amount.
#

# Cutout
partLeft = Cutout(CircleElement(5.0))
partCenter = Cutout(RectangleElement(10.0, 5.0))
partRight = Cutout(SlotElement(10.0, 5.0), rib=Faceplate.STD_RIB)

# A basic faceplate with row layout
plate = Faceplate(
    rack_units=1.0,
    features=[[partLeft, partCenter, partRight]],
    layout=RowLayout(place=Dir2.SIDE_BOTTOM),
).render()

# Show the plate in the OCP viewer
plate.show()

# Export the plate as a STEP file as well
plate.export_step("outputs/face_plate_with_div.step")
