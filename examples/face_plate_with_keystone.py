from importlib.resources import as_file, files
import build123d as bd
from ocp_vscode import show

from mini_rack_printables import ImportPart, Div, FacePlate

#
# This example demonstrates a face plate with a keystone cutout.
#

# A basic Div with horizontal layout and evenly divided sections for 3 keystones
with as_file(files("mini_rack_printables.assets") / "keystone.brep") as keystone_path:
    keystone_part = ImportPart(keystone_path, size=bd.Vector(17.7, 25, 9.75))
    div = Div(parts=[keystone_part for _ in range(3)])
    plate = FacePlate(
        rack_units=1.0,
        part=div,
    ).render()

# Show the plate in the OCP viewer
show(plate)

# Export the plate as a STEP file as well
bd.export_step(plate, "outputs/face_plate_with_keystone.step")
