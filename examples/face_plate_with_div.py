import build123d as bd
from ocp_vscode import show

from mini_rack_printables import Cutout, CutoutType, Div, FacePlate, RcAlignment

#
# This example demonstrates a face plate with a Div layout containing 3 cutouts.
# Each cutout has a different alignment and padding and shift amount.
#

# Define a basic cutout
partCenter = Cutout(CutoutType.RECTANGLE, size=bd.Vector(10.0, 5.0))

# Show what alignment and padding does
partLeft = Cutout(CutoutType.CIRCLE, radius=5.0, align=RcAlignment.TOP, padding=1.0)

# Show that a shift can be used to move the shape outside of its bounding box.
# In this case, the cutout rib is merged with the plate rib.
# Shift when used with caution, it can be powerful feature
#
partRight = Cutout(
    CutoutType.SLOT,
    size=bd.Vector(10.0, 5.0),
    align=RcAlignment.BOTTOM,
    shift=bd.Vector(0, -1),
    rib_size=FacePlate.STD_RIB,
)

# A basic Div with horizontal layout and evenly divided sections
div = Div([partLeft, partCenter, partRight])

plate = FacePlate(
    rack_units=1.0,
    rib_size=FacePlate.STD_RIB,
    part=div,
).render()

# Show the plate in the OCP viewer
show(plate)

# Export the plate as a STEP file as well
bd.export_step(plate, "outputs/face_plate_with_div.step")
