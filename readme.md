# Mini-Rack Printables

A Python library for creating 3d printable models for enclosing many different gadgets. As many good models already exist, this project provides more customizilibilty through a library of cutouts and holders with a flexible layout system. The envisioned composible system include:

- Shelves, face plates, and enclosures
- Rectangular and circular cutouts as well as arbritary shapes described an SVG file
- Component holders for common shapes as well as arbritary shapes described in an SVG or STL file


## Example code

To use look at the model and feature packages for existing support devices. Defined the specific
model wanted by adjusting the parameters. 

```python
from mini_rack_printables import Keystone, faceplate, FaceplateStyle
#
# This example demonstrates a 10-inch rack faceplate with a 3 network keystone cutouts.
#

# A 1u faceplace with ribs and one row with 3 network keystone cutouts. 
model = faceplate(
    rack_units=1.0, 
    style=FaceplateSytle(rib=FaceplateSytle.STD_RIB),
    features=[[Keystone()] * 3]
)

# Show the model in the OCP viewer
model.show()

# Export the model as a STEP file as well
model.export_step("outputs/faceplate_with_keystone.step")
```

## Directory Structure

The project directory structure is as follows:

- `src/mini_rack_printables/` - the main library source code
- `src/mini_rack_printables/models/` - models are the starting point for creating 3d printable models.
- `src/mini_rack_printables/features/` - reusable building blocks that enhance models.
- `src/mini_rack_printables/core` - core code used by models and features
- `src/mini_rack_printables/assets/` - Assets for common 3d printable models in this space. 
- `examples/` - example scripts for creating 3d printable models that use the library
- `scripts/` - scripts for building and testing the library.
- `tests/` - test scripts for verifying the library's functionality
- `outputs/` - directory for storing the output models in STEP or STL format.
- `taskfile.yml` - common task definitions for the project.


 ## TODO

 To make a reasonable library requires

  - [x] Convert to python and build123d
  - [x] WalledHolder, PuckHolder, CornerHolder parts 
  - [x] Shelves
  - [x] ValueErrors instead of asserts
  - [ ] SVG primative 
  - [x] Fill pattern for primatives using intersections
  - [x] Layout redesign with spacers 
  - [x] Holders for shelves
  - [ ] Extract pictures for the readme
  - [ ] Documentation add more examples and usage instructions. Seperated the programming stuff. 
  - [ ] Assembler: bound box
  - [x] Model -> functions
  - [ ] Look at import style standard (consider the google style)
