# Layout tests
#
from mini_rack_printables import RackDims, RackScrewDims, layout_rack_screw_holes


def test_layout_rack_screw_holes_1u() -> None:
    values = layout_rack_screw_holes(rack_units=1.0)

    assert len(values) == 6
    assert values[0] == RackScrewDims.BOTTOM
    assert values[1] == RackScrewDims.MIDDLE
    assert values[2] == RackScrewDims.TOP


def test_layout_rack_screw_holes_3u() -> None:
    values = layout_rack_screw_holes(rack_units=3.0)

    assert len(values) == 18
    assert values[0] == RackScrewDims.BOTTOM
    assert values[1] == RackScrewDims.MIDDLE
    assert values[8] == RackScrewDims.TOP + 2 * RackDims.HEIGHT_1U


def test_layout_rack_screw_holes_2u_without_middle_holes() -> None:
    values = layout_rack_screw_holes(rack_units=2.0, middle_holes=False)

    assert len(values) == 8
    assert values[0] == RackScrewDims.BOTTOM
    assert values[1] == RackScrewDims.TOP
    assert values[3] == RackScrewDims.TOP + 1 * RackDims.HEIGHT_1U


def test_layout_rack_screw_holes_half_u() -> None:
    values = layout_rack_screw_holes(rack_units=0.5)

    assert len(values) == 4
    assert values[0] == RackScrewDims.BOTTOM
    assert values[1] == RackScrewDims.MIDDLE


def test_layout_rack_screw_holes_1_5u() -> None:
    values = layout_rack_screw_holes(rack_units=1.5)

    assert len(values) == 10
    assert values[0] == RackScrewDims.BOTTOM
    assert values[1] == RackScrewDims.MIDDLE
    assert values[4] == RackScrewDims.MIDDLE + RackDims.HEIGHT_1U


def test_layout_rack_screw_holes_half_u_bottom_aligned() -> None:
    values = layout_rack_screw_holes(rack_units=0.5, half_height_bottom=True)

    assert len(values) == 4
    assert values[0] == RackScrewDims.MIDDLE - RackDims.HEIGHT_1U / 2
    assert values[1] == RackScrewDims.TOP - RackDims.HEIGHT_1U / 2


def test_layout_rack_screw_holes_1u_bottom_aligned() -> None:
    values = layout_rack_screw_holes(rack_units=1.0, half_height_bottom=True)

    assert len(values) == 8
    assert values[0] == RackScrewDims.MIDDLE - RackDims.HEIGHT_1U / 2
    assert values[1] == RackScrewDims.TOP - RackDims.HEIGHT_1U / 2
    assert values[2] == RackScrewDims.BOTTOM + RackDims.HEIGHT_1U / 2
    assert values[3] == RackScrewDims.MIDDLE + RackDims.HEIGHT_1U / 2
