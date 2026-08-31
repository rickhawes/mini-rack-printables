import build123d as bd
from ocp_vscode import show

from mini_rack_printables import Shelf

#
# This example demonstrates a basic shelf with default settings.
#

shelf = Shelf(rack_units=1.0).render()

# Show the shelf in the viewer. Run 'task viewer' before.
show(shelf)

# Export the plate to a STEP file
bd.export_step(shelf, "outputs/basic_shelf.step")
