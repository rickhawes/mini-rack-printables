import build123d as bd
from ocp_vscode import show

from mini_rack_printables import Holder, FacePlate, Div, HolderStyle

#
# This example demonstrates a face plate with a Jet KVM cutout.
#
holder = Holder(style=HolderStyle.BACK_LIP, device_size=(212.8, 33.1, 30))
plate = FacePlate(rack_units=1.0, part=Div(parts=[holder]), rib_size=FacePlate.STD_RIB).render()

# Show the plate in the OCP viewer
show(plate)

# Export the plate as a STEP file as well
bd.export_step(plate, "outputs/face_plate_with_holder.step")
