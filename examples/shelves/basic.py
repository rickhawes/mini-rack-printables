from mini_rack_printables import Shelf

#
# This example demonstrates a basic shelf with default settings.
#

shelf = Shelf(rack_units=1.0).render()

# Show the shelf in the viewer. Run 'task viewer' before.
shelf.show()

# Export the plate to a STEP file
shelf.export_step("outputs/basic_shelf.step")
