import build123d as bd
from ocp_vscode import show

from mini_rack_printables import Cutout, CutoutType, Div, FacePlate, RcAlignment

rib_size = bd.Vector(2.0, 1.0)

partTop = Cutout(CutoutType.CIRCLE, radius=5.0, align=RcAlignment.TOP, padding=1.0)

partCenter = Cutout(CutoutType.RECTANGLE, size=bd.Vector(10.0, 5.0))

partBottom = Cutout(CutoutType.SLOT, size=bd.Vector(10.0, 5.0), align=RcAlignment.BOTTOM, rib_size=rib_size)

part = FacePlate(
    rack_units=1.0,
    thickness=3.5,
    middle_holes=True,
    half_alignment=False,
    rib_size=rib_size,
    part=Div([partTop, partCenter, partBottom]),
).render()

show(part)

bd.export_step(part, "outputs/face_plate_with_div.step")
