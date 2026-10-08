import build123d as bd
from ocp_vscode import show

from mini_rack_printables import CircleElement, Cutout, Faceplate

#
# Minimal example of a faceplate with a circle cutout feature
#

plate = Faceplate(
    rack_units=1.0,
    features=[[Cutout(CircleElement(10.0), rib=Faceplate.STD_RIB)]]
).render()

plate.show()

plate.export("outputs/face_plate_with_cutout.step")
