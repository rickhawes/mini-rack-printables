import build123d as bd
from ocp_vscode import show
from importlib.resources import files, as_file

from mini_rack_printables import XRayModel, ImportPart

#
# This example demonstrates a keystone cutout.
#
with as_file(files("mini_rack_printables.assets").joinpath("keystone.brep")) as path:
    plate = XRayModel(
        part=ImportPart(path=path.absolute(), size=bd.Vector(17.7, 25, 9.75))
    ).render()

# Show the plate in the OCP viewer
show(plate)
