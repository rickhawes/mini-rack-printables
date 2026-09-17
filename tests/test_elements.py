from build123d import Axis
from mini_rack_printables import (
    Place,
    Element2D,
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
    RightTriangleElement,
    TrapezoidElement,
)
# test by rendering a bunch of elements

RECT = "Rectangle tests"
FILL = "Fill tests"
SHAPE = "Shape tests"


def test_rectangle_element(viewer_logger):
    elem = RectangleElement(width=40, height=20)
    viewer_logger.log(elem.sketch(), RECT)


def test_rounded_corners(viewer_logger):
    elem = RectangleElement(width=40, height=20, corners=4)
    viewer_logger.log(elem.sketch(), RECT)


def test_inset_corners(viewer_logger):
    elem = RectangleElement(40, 20, InsetCorners(5))
    viewer_logger.log(elem.sketch(), RECT)


def test_beveled_corners(viewer_logger):
    elem = RectangleElement(40, 20, BeveledCorners(4, 6))
    viewer_logger.log(elem.sketch(), RECT)


def test_selected_corners(viewer_logger):
    elem = RectangleElement(
        40, 20, SelectedCorners(RoundedCorners(6), top_left=True, bottom_right=True)
    )
    viewer_logger.log(elem.sketch(), RECT)


def test_hex_fill(viewer_logger):
    elem = RectangleElement(width=40, height=20, fill=HexHoles())
    viewer_logger.log(elem.sketch(), FILL)
    elem = RectangleElement(width=40, height=20, corners=4, fill=HexHoles())
    viewer_logger.log(elem.sketch(), FILL)


def test_empty_fill(viewer_logger):
    elem = RectangleElement(width=40, height=10, corners=4, fill=HexHoles())
    viewer_logger.log(elem.sketch(), FILL)


def test_circular_fill(viewer_logger):
    elem = RectangleElement(width=40, height=20, fill=CircleHoles())
    viewer_logger.log(elem.sketch(), FILL)
    elem = RectangleElement(width=40, height=20, corners=4, fill=CircleHoles())
    viewer_logger.log(elem.sketch(), FILL)


def test_square_fill(viewer_logger):
    elem = RectangleElement(width=40, height=20, fill=SquareHoles())
    viewer_logger.log(elem.sketch(), FILL)


def test_circle_element(viewer_logger):
    elem = CircleElement(radius=10)
    viewer_logger.log(elem.sketch(), SHAPE)


def test_slot_element(viewer_logger):
    elem = SlotElement(40, 20)
    viewer_logger.log(elem.sketch(), SHAPE)


def test_trapezoid_element(viewer_logger):
    e1 = TrapezoidElement(40, 20, angle1=80)
    viewer_logger.log(e1.sketch(), SHAPE)
    e2 = TrapezoidElement(40, 20, minor_width=10, angle1=90)
    viewer_logger.log(e2.sketch(), SHAPE)
    e3 = TrapezoidElement(40, 20, minor_width=10, angle1=90, rotate=90)
    viewer_logger.log(e3.sketch(), SHAPE)


def test_right_triangle_element(viewer_logger):
    elem = RightTriangleElement(width=40, height=20)
    viewer_logger.log(elem.sketch(), SHAPE)
    elem2 = RightTriangleElement(width=40, height=20, flip=True)
    viewer_logger.log(elem2.sketch(), SHAPE)


def test_combine_elements(viewer_logger):
    e1 = RectangleElement(5, 2)
    e2 = TrapezoidElement(10, 15, minor_width=2, angle1=90, rotate=90)
    e3 = RectangleElement(20, 10)
    sk = Element2D.combine([e1, e2, e3], axis=Axis.X, anchor=Place.BOTTOM)
    viewer_logger.log(sk, SHAPE)
