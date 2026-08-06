import build123d as bd
from ocp_vscode import show

from mini_rack_printables import FacePlate, Cutout

rib_size = bd.Vector(2.0, 1.0)

part = FacePlate(
    rack_units=1.0,
    thickness=3.5,
    middle_holes=True,
    half_alignment=False,
    rib_size=rib_size,
    part=Cutout(10, rib_size=rib_size),
).render()

show(part)

bd.export_step(part, "outputs/face_plate_with_cutout.step")
