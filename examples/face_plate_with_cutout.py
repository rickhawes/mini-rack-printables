import build123d as bd
from ocp_vscode import show

from mini_rack_printables import FacePlate, Cutout, CircleElement

#
# Minimal example of a face plate with a part
#

plate = FacePlate(
    rack_units=1.0,
    part=Cutout(CircleElement(10.0)),
).render()

show(plate)

bd.export_step(plate, "outputs/face_plate_with_cutout.step")
