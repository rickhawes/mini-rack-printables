# Layout tests
# 
from mini_rack_printables import layout_rack_screw_holes, RackScrewDims, RackDims

def test_layout_rack_screw_holes_1u():
	values = layout_rack_screw_holes(rack_units = 1.0)
	
	assert len(values) == 3
	assert values[0] == RackScrewDims.BOTTOM
	assert values[1] == RackScrewDims.MIDDLE
	assert values[2] == RackScrewDims.TOP

def test_layout_rack_screw_holes_3u():
    values = layout_rack_screw_holes(rack_units=3.0)

    assert len(values) == 9
    assert values[0] == RackScrewDims.BOTTOM
    assert values[1] == RackScrewDims.MIDDLE
    assert values[8] == RackScrewDims.TOP + 2 * RackDims.HEIGHT_1U


def test_layout_rack_screw_holes_2u_without_middle_holes():
    values = layout_rack_screw_holes(rack_units=2.0, middle_holes=False)

    assert len(values) == 4
    assert values[0] == RackScrewDims.BOTTOM
    assert values[1] == RackScrewDims.TOP
    assert values[3] == RackScrewDims.TOP + 1 * RackDims.HEIGHT_1U


def test_layout_rack_screw_holes_half_u():
    values = layout_rack_screw_holes(rack_units=0.5)

    assert len(values) == 2
    assert values[0] == RackScrewDims.BOTTOM
    assert values[1] == RackScrewDims.MIDDLE


def test_layout_rack_screw_holes_1_5u():
    values = layout_rack_screw_holes(rack_units=1.5)

    assert len(values) == 5
    assert values[0] == RackScrewDims.BOTTOM
    assert values[1] == RackScrewDims.MIDDLE
    assert values[4] == RackScrewDims.MIDDLE + RackDims.HEIGHT_1U


def test_layout_rack_screw_holes_half_u_bottom_aligned():
    values = layout_rack_screw_holes(rack_units=0.5, bottom_is_half_height=True)

    assert len(values) == 2
    assert values[0] == RackScrewDims.MIDDLE - RackDims.HEIGHT_1U / 2
    assert values[1] == RackScrewDims.TOP - RackDims.HEIGHT_1U / 2


def test_layout_rack_screw_holes_1u_bottom_aligned():
    values = layout_rack_screw_holes(rack_units=1.0, bottom_is_half_height=True)

    assert len(values) == 4
    assert values[0] == RackScrewDims.MIDDLE - RackDims.HEIGHT_1U / 2
    assert values[1] == RackScrewDims.TOP - RackDims.HEIGHT_1U / 2
    assert values[2] == RackScrewDims.BOTTOM + RackDims.HEIGHT_1U / 2
    assert values[3] == RackScrewDims.MIDDLE + RackDims.HEIGHT_1U / 2
