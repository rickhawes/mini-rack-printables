from mini_rack_printables import (
    RectangleElement,
    FillPattern,
    CircleElement,
    SlotElement,
    CrossElement,
)
# test by rendering a bunch of elements


def test_rectangle_element(viewer_logger):
    elem = RectangleElement(width=40, height=20)
    viewer_logger.log(elem.sketch())


def test_rectangle_rounded_element(viewer_logger):
    elem = RectangleElement(width=40, height=20, radius=2)
    viewer_logger.log(elem.sketch())


def test_hex_fill(viewer_logger):
    elem = RectangleElement(width=40, height=20, radius=0, fill=FillPattern.HEX)
    viewer_logger.log(elem.sketch())
    elem = RectangleElement(width=40, height=20, radius=4, fill=FillPattern.HEX)
    viewer_logger.log(elem.sketch())


def test_circular_fill(viewer_logger):
    elem = RectangleElement(width=40, height=20, radius=0, fill=FillPattern.CIRCULAR)
    viewer_logger.log(elem.sketch())
    elem = RectangleElement(width=40, height=20, radius=4, fill=FillPattern.CIRCULAR)
    viewer_logger.log(elem.sketch())


def test_square_fill(viewer_logger):
    elem = RectangleElement(width=40, height=20, radius=4, fill=FillPattern.SQUARE)
    viewer_logger.log(elem.sketch())


def test_circle_element(viewer_logger):
    elem = CircleElement(radius=10)
    viewer_logger.log(elem.sketch())


def test_slot_element(viewer_logger):
    elem = SlotElement(40, 20)
    viewer_logger.log(elem.sketch())


def test_cross_element(viewer_logger):
    elem = CrossElement(40, 20, 5, 5)
    viewer_logger.log(elem.sketch())
