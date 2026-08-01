import build123d as bd
from ocp_vscode import show

from mini_rack_printables import FacePlate

part = FacePlate(
    rack_units=1.0,
    thickness=3.5,
    middle_holes=True,
    half_alignment=False,
    rib_size=bd.Vector(2.0, 1.0),
).render()

show(part)

bd.export_step(part, "outputs/blank_face_plate.step")
