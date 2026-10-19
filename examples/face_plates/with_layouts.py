import build123d as bd
from ocp_vscode import show

from mini_rack_printables import (
    CircleElement,
    Cutout,
    Dir2,
    FacePlate,
    RectangleElement,
    RowLayout,
    SlotElement,
)

#
# This example demonstrates a face plate with a RowLayout containing 3 cutouts.
# Each cutout has a different alignment and padding and shift amount.
#

# Cutout
partLeft = Cutout(CircleElement(5.0))
partCenter = Cutout(RectangleElement(10.0, 5.0))
partRight = Cutout(SlotElement(10.0, 5.0), rib=FacePlate.STD_RIB)

# A basic face plate with row layout
plate = FacePlate(
    rack_units=1.0,
    features=[partLeft, partCenter, partRight],
    layout=RowLayout(place=Dir2.BOTTOM),
).render()

# Show the plate in the OCP viewer
show(plate)

# Export the plate as a STEP file as well
bd.export_step(plate, "outputs/face_plate_with_div.step")
