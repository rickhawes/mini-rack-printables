from mini_rack_printables import (
    InsetCorners,
    HexHoles,
    SquareHoles,
    CircleHoles,
    RectangleElement,
    CircleElement,
    SlotElement,
    BeveledCorners,
    SelectedCorners,
    RoundedCorners,
)
# test by rendering a bunch of elements


def test_rectangle_element(viewer_logger):
    elem = RectangleElement(width=40, height=20)
    viewer_logger.log(elem.sketch())


def test_rectangle_rounded_element(viewer_logger):
    elem = RectangleElement(width=40, height=20, corners=4)
    viewer_logger.log(elem.sketch())


def test_hex_fill(viewer_logger):
    elem = RectangleElement(width=40, height=20, fill=HexHoles())
    viewer_logger.log(elem.sketch())
    elem = RectangleElement(width=40, height=20, corners=4, fill=HexHoles())
    viewer_logger.log(elem.sketch())


def test_circular_fill(viewer_logger):
    elem = RectangleElement(width=40, height=20, fill=CircleHoles())
    viewer_logger.log(elem.sketch())
    elem = RectangleElement(width=40, height=20, corners=4, fill=CircleHoles())
    viewer_logger.log(elem.sketch())


def test_square_fill(viewer_logger):
    elem = RectangleElement(width=40, height=20, fill=SquareHoles())
    viewer_logger.log(elem.sketch())


def test_circle_element(viewer_logger):
    elem = CircleElement(radius=10)
    viewer_logger.log(elem.sketch())


def test_slot_element(viewer_logger):
    elem = SlotElement(40, 20)
    viewer_logger.log(elem.sketch())


def test_cross_element(viewer_logger):
    elem = RectangleElement(40, 20, InsetCorners(5))
    viewer_logger.log(elem.sketch())


def test_beveled_corners(viewer_logger):
    elem = RectangleElement(40, 20, BeveledCorners(4, 6))
    viewer_logger.log(elem.sketch())


def test_selected_corners(viewer_logger):
    elem = RectangleElement(
        40, 20, SelectedCorners(RoundedCorners(6), top_left=True, bottom_right=True)
    )
    viewer_logger.log(elem.sketch())
