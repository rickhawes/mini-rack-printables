import build123d as bd
from ocp_vscode import show

from mini_rack_printables import FacePlate

fp = FacePlate(
    rack_units=1.0,
    thickness=3.5,
    middle_holes=True,
    half_alignment=False,
)



show(fp.render())