# Mini-Rack Printables

This project creates 3d printable models for mini server racks based on the 10-inch standard.
As many good models already exist, this project provides more customizilibilty through a extensible set of cutouts and holders with a flexible layout system.
The envisioned system for features include:

- Rectangular and circular cutouts as well as arbritary shapes described an SVG file
- Component holders for common shapes as well as arbritary shapes described in an SVG or STL file
- Honeycomb and slats holes for venting
- System of layouts

## Assembly and parts

The project works by first describing a 3d model using a series functions to create descriptions of assemblies. Assembilies exist for rack shelves, rack plates and cable ties. Assemblies are then rendered into model using the 'render' module.

A plate assembly can contain parts. Parts model customizations for a rack face plate or a rack shelf. A special type of part is called a layout. Layouts divide a parent part into divisions for the layout's contained parts.  

## Naming Conventions

Terms commomly used in all modules. Names are chosen to not conflict with SCAD and BOSL2 functions and modules.

- x, y, z - coordinates in space.
- assembly - a model that is stands on its own.
- size - a [dx, dy] or a [dx, dy, dz] vector with dimensions of a volume 2d or 3d. Always positive.
- plate - the side, bottom, back or face plate of the rack.
- part - features on a plate implemented by a polymorphic struct.
- subpart - a part can contain sub-parts which are just parts.
- section - the section of a plate that holds a part.
- padding - a single distance or a vector of distances for an outset, always positive.
- rc - A [dx, dy] or a [x, y, dx, dy] vector defining a 2d area in space.
- cu - A [dx, dy, dz] or a [x, y, z, dx, dy, dz] vector defining a 3d volume in space.
