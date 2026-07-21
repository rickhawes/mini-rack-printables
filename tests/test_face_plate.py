# Layout tests
# 
from mini_rack_printables import layout_rack_screw_holes, RackScrewDims

def test_layout_rack_screw_holes_1u():
	values = layout_rack_screw_holes(rack_units = 1.0)
	
	assert len(values) == 3
	assert values[0] == RackScrewDims.BOTTOM
	assert values[1] == RackScrewDims.MIDDLE
	assert values[2] == RackScrewDims.TOP