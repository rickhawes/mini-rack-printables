import build123d as bd
from ocp_vscode import show

from mini_rack_printables import JetKVM, FacePlate

#
# This example demonstrates a face plate with a Jet KVM cutout.
#
plate = FacePlate(rack_units=1.0, part=JetKVM(), rib=FacePlate.STD_RIB).render()

# Show the plate in the OCP viewer
show(plate)

# Export the plate as a STEP file as well
bd.export_step(plate, "outputs/face_plate_with_jetkvm.step")
