# Mini-Rack Printables

A Python library for creating 3d printable models for mini server racks based on the 10-inch standard. As many good models already exist, this project provides more customizilibilty through a library of cutouts and holders with a flexible layout system. The envisioned composible system include:

- Shelves, face plates
- Rectangular and circular cutouts as well as arbritary shapes described an SVG file
- Component holders for common shapes as well as arbritary shapes described in an SVG or STL file
- Honeycomb and slats holes for venting
- Layouts inspired by HTML Div system

## Directory Structure

The project directory structure is as follows:

- `src/mini_rack_printables/` - the main library source code
- `src/mini_rack_printables/models/` - models are the starting point for creating 3d printable models.
- `src/mini_rack_printables/parts/` - parts are reusable building blocks that enhance models.
- `src/mini_rack_printables/assets/` - Assets for common 3d printable models in this space. 
- `examples/` - example scripts for creating 3d printable models that use the library
- `scripts/` - scripts for building and testing the library.
- `tests/` - test scripts for verifying the library's functionality
- `outputs/` - directory for storing the output models in STEP or STL format.
- `taskfile.yml` - common task definitions for the project.

## Naming Conventions

Terms commomly used in the project

- x, y, z - coordinates in space.
- model - a model that is stands on its own.
- part - a part is a feature on a plate that can be added or subtracted from the model's geometry.
- size - a [dx, dy] or a [dx, dy, dz] vector with dimensions of a volume 2d or 3d. Always positive.
- plate - the side, bottom, back or face plate of the rack.
- section - the section of a plate that holds a part.
- padding - a single distance for an outset, always positive.
- rc - A pair of size [dx, dy] and [x, y] vector defining a 2d area in space.
- rib - A rib outlines a 2d area on a plate for extra strength. It has depth and width.
- wall - A wall of a shape can have patterns for venting. 

## Coordinates

Models are oriented for 3d printing. They are centered in the XY plane and with solids extruded in the positive Z direction. This is the default of build123d library. Parts are centered in the local coordinate in the XY plane as well. 

Terms like `width`, `height`, `depth`, `top`, `bottom`, `front`, `back`, `left`, `right` are used in reference to this XYZ orientation. In other words, `left` refers to the negative X direction, `right` refers to the positive X direction, and so on. 

## Choices 

 The project was originally coded in OpenSCAD and BOSL2 which is a common choice in the 3d printing community, but was ported to Python for better software development tools and language features. [build123d](https://github.com/build123d/build123d) was selected for base framework because it has good documentation and an intuitive API for creating 3d models. Every tool and framework choice has its trade-offs, but these choices ended up being the best for the author's enjoyment. 

 ## TBD

 To make a reasonable library requires

  - [x] Convert to python and build123d
  - [x] WalledHolder, PuckHolder, CornerHolder parts 
  - [ ] Shelves
  - [ ] SVG primative 
  - [ ] Fill pattern for primatives using intersections
  - [ ] Layout redesign with spacers 
  - [ ] Holders for shelves
  - [ ] Extract pictures for the readme
  - [ ] Documentation add more examples and usage instructions. Seperated the programming stuff. 
