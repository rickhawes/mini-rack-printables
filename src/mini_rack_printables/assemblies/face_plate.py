from ..dimensions import RackDims, RackScrewDims
import math

# ------------------------------------------------------------------------------------------------
# Face Plate
# ------------------------------------------------------------------------------------------------

# Width of the tab hole found  (use 10-24 screw hole diameter for height)
SHELF_TAB_HOLE_WIDTH_TECMOJO = 9.28
# Rounding applied to corners of a face_plate
FACE_PLATE_ROUNDING = 3.0


def layout_rack_screw_holes(
    rack_units: float, middle_holes: bool = True, bottom_is_half_height: bool = False
) -> list[float]:
    """
    Layout an

    Args:
            rack_units: Number of rack units of the plate with half units being acceptable
            middle_holes: draw middle screw holes
            bottom_is_half_height: The bottom will start on the middle hole

    Returns:
            A list of offsets
    """
    bottom_half_units = 1 if bottom_is_half_height else 0
    full_units = (
        math.floor(rack_units - 0.5)
        if bottom_is_half_height
        else math.floor(rack_units)
    )
    top_half_units = 1 if (rack_units - bottom_half_units * 0.5 - full_units > 0) else 0
    offsets: list[float] = []

    # Construct the y values for the holes from 0 to height

    # bottom half units
    if bottom_half_units:
        if middle_holes:
            offsets.extend(
                [
                    RackScrewDims.MIDDLE - RackDims.HEIGHT_1U / 2,
                    RackScrewDims.TOP - RackDims.HEIGHT_1U / 2,
                ]
            )
        else:
            offsets.append(RackScrewDims.TOP - RackDims.HEIGHT_1U / 2)

    # middle full units
    for u in range(full_units):
        y_slot = u * RackDims.HEIGHT_1U + bottom_half_units * RackDims.HEIGHT_1U / 2
        if middle_holes:
            offsets.extend(
                [
                    RackScrewDims.BOTTOM + y_slot,
                    RackScrewDims.MIDDLE + y_slot,
                    RackScrewDims.TOP + y_slot,
                ]
            )
        else:
            offsets.extend([RackScrewDims.BOTTOM + y_slot, RackScrewDims.TOP + y_slot])

    # top half units
    if top_half_units:
        y_slot = (
            RackDims.HEIGHT_1U * full_units + bottom_half_units * RackDims.HEIGHT_1U / 2
        )
        if middle_holes:
            offsets.extend(
                [RackScrewDims.BOTTOM + y_slot, RackScrewDims.MIDDLE + y_slot]
            )
        else:
            offsets.extend([RackScrewDims.BOTTOM + y_slot])

    return offsets


scad = """
= flatten(
		let (
			bottom_half_units = bottom_is_half_height ? 1 : 0,
			full_units = bottom_is_half_height ? floor(rack_units - 0.5) : floor(rack_units),
			top_half_units = rack_units - bottom_half_units*0.5 - full_units > 0 ? 1 : 0
		)
		[
			// Construct the y values for the holes from 0 to height
			//
			// bottom half units
			for(u = 0; u < bottom_half_units; u = u+1)
				if (middle_holes) 
					[RackScrewDims.MIDDLE - RackDims.HEIGHT_1U/2, RackScrewDims.TOP - RackDims.HEIGHT_1U/2] 
				else
					[RackScrewDims.TOP - RackDims.HEIGHT_1U/2],
			
			// middle full units
			for(u = 0; u < full_units; u = u+1)
				let(y_slot = u*RackDims.HEIGHT_1U + bottom_half_units*RackDims.HEIGHT_1U/2)
				if (middle_holes)
					[RackScrewDims.BOTTOM+y_slot, RackScrewDims.MIDDLE+y_slot, RackScrewDims.TOP+y_slot]
				else
					[RackScrewDims.BOTTOM+y_slot, RackScrewDims.TOP+y_slot],
			
			// top half units 
			for(u = 0; u < top_half_units; u = u+1)
				let(y_slot = RackDims.HEIGHT_1U*full_units + bottom_half_units*RackDims.HEIGHT_1U/2)
				if (middle_holes)
					[RackScrewDims.BOTTOM+y_slot, RackScrewDims.MIDDLE+y_slot]
				else
					[RackScrewDims.BOTTOM+y_slot]
				 
		]
	)


def face_plate(
	rack_units, 
	thickness, 
	middle_holes = True, 
	half_alignment = False, 
	rib_size = [0,0],
	part = None
)
	Draw a face plate assembly. 

	Args:
		amount: The total cash amount to deduct from the balance.

	Returns:
		the model object for a face plate

	Raises:
		ValueError: If the amount is negative or exceeds the balance.
	

	assert(is_num(rack_units) && rack_units > 0)
	assert(is_num(thickness) && thickness > 0)
	assert(is_undef(part) || is_part(part))
	object(
		assembly_base(FACE_PLATE_TYPE), 
		rack_units = rack_units,
		thickness = thickness,
		middle_holes = middle_holes,
		half_alignment = half_alignment,
		rib_size = rib_size,
		part = part
	);

// Is the passed struct a face plate?
function is_face_plate(plate)   = plate.assembly_type == FACE_PLATE_TYPE;

// Layout the screw holes


// Render the face plate defined by fp
module _render_face_plate(fp) {
	assert(is_face_plate(fp));
	rack_units              = fp.rack_units;
	thickness               = fp.thickness;
	middle_holes            = fp.middle_holes;
	half_alignment          = fp.half_alignment;
	rib_size                = fp.rib_size;
	part                    = fp.part; 

	module rack_screw_holes(
		rack_units,
		face_plate_thickness, 
		middle_holes = true,
		bottom_is_half_height = false
	) {
		assert(!is_undef(rack_units), "rack_units is undefined");
		height = rack_units * RackDims.HEIGHT_1U;

		module one_hole(face_plate_thickness) {
			attachable() {
				linear_extrude(height = face_plate_thickness) 
					slot_xaxis(shelf_tab_hole_width_tecmojo, screw_hole_10_32/2);
				children();
			}
		}

		module right_tab() {
			translate([rack_screw_dx/2, -height/2, 0]) {
				y_values = layout_rack_screw_holes(rack_units, middle_holes, bottom_is_half_height);
				for (y = y_values) {
					translate([0, y])
						one_hole(face_plate_thickness);
				}
			}
		}

		right_tab();
		xflip()
			right_tab(); 
	}

	module face_plate_ribs(plate_size, part_size, rib_size) {
		tag("rib") 
		align(TOP, [FRONT, BACK]) 
			prismoid(size2=[part_size.x, rib_size.x], h=rib_size.y, xang=30, yang=90);
	}

	module plain_plate(plate_size, rib_size) {
		diff() {
			extruded_roundrect(plate_size, r = face_plate_rounding, anchor=TOP) {
				// Ribs on top and bottoms 
				if (rib_size.y > 0) {
					tag("keep")
					face_plate_ribs(plate_size, part_area_size, rib_size);
				}
	
				// Rack Screw
				tag("remove")
				align(BOTTOM) {
					rack_screw_holes(rack_units, thickness, middle_holes, half_alignment);
				}

				children();
			}
		}
	}

	// Layout calculations
	plate_size = [
		rack_width_10inch, 
		rack_units * RackDims.HEIGHT_1U, 
		thickness
	];
	part_area_size = [
		plate_size.x - 2*shelf_tab_width_tecmojo - 2*rib_size.x, 
		plate_size.y - 2*rib_size.x, 
		thickness
	];

	// Render the plate
	plain_plate(plate_size, rib_size) {
		if (!is_undef(part)) {
			render_part(part, part_area_size);
		}
	}
}
"""
