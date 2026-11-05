"""This example demonstrates a basic shelf with default settings."""

from mini_rack_printables import shelf

shelf = shelf(rack_units=1.0)

# Show the shelf in the viewer. Run 'task viewer' before.
shelf.show()

# Export the shelf to a STEP file
shelf.export_step("outputs/basic_shelf.step")
