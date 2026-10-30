from mini_rack_printables.core.piece import Piece
from typing import override
from build123d import Vector

from mini_rack_printables import (
    Assembler,
    AxDir3,
    BoxElement,
    Bx,
    Dir2,
    Feature,
    ModelLogger,
    Rc,
    Vec2,
    Vec3,
)


def test_make() -> None:
    base = Bx(100, 100, 10, 0, 0, 5)

    # on the top side of the base
    m1 = Assembler.make(base)
    assert m1.origin == Vec3(0, 0, 10)
    assert m1.plane_rc == Rc(100, 100)
    assert m1.plane_depth == 10
    assert m1.side == AxDir3.Z_PLUS
    assert m1._plane.location.position == Vector(0, 0, 10)
    assert m1._plane.z_dir == Vector(0, 0, 1)

    # on the right side of the base pointing outward
    m2 = Assembler.make(base, side=AxDir3.X_PLUS)
    assert m2.origin == Vec3(50, 0, 5)
    assert m2.plane_rc == Rc(100, 10)
    assert m2.plane_depth == 100
    assert m2.side == AxDir3.X_PLUS
    assert m2._plane.location.position == m2.origin.to_vector()
    assert m2._plane.z_dir == Vector(1, 0, 0)


def test_make_with_element() -> None:
    base = BoxElement(100, 100, 10)

    m1 = Assembler.make_with_element(base)
    assert m1.origin == Vec3(0, 0, 10)
    assert m1.plane_rc == Rc(100, 100)
    assert m1.plane_depth == 10
    assert m1.side == AxDir3.Z_PLUS
    assert m1._plane.location.position == Vector(0, 0, 10)
    assert m1._plane.z_dir == Vector(0, 0, 1)

    # on the right side of the base pointing outward
    m2 = Assembler.make_with_element(base, side=AxDir3.X_PLUS)
    assert m2.origin == Vec3(50, 0, 5)
    assert m2.plane_rc == Rc(100, 10)
    assert m2.plane_depth == 100
    assert m2.side == AxDir3.X_PLUS
    assert m2._plane.location.position == m2.origin.to_vector()
    assert m2._plane.z_dir == Vector(1, 0, 0)


def test_assemble_two_boxes(viewer_logger: ModelLogger) -> None:
    base = BoxElement(30, 20, 10)
    node = BoxElement(2, 1.5, 1)

    # place the nodes at all 9 places on the assembler's plane
    def place_boxes(maker: Assembler) -> None:
        for member in Dir2:
            if member.value == Dir2.CORNER_LF_BT.value:
                cut = True
                offset = Vec3(0, 0, -1)
            else:
                cut = False
                offset = Vec3(0, 0, 0)
            maker.place_element(
                node, Assembler.Place(origin=Dir2(member.value), offset=offset), cut
            )

    # place the nodes on the base using a assembler
    m1 = Assembler.make_with_element(base, side=AxDir3.TOP)
    place_boxes(m1)
    viewer_logger.log(m1.make_rendering().part)

    # different side and orientation, but the same placement code works as expected.
    # notice that the placed nodes have an orientation that matches the side's orientation
    m2 = Assembler.make_with_element(base, side=AxDir3.Z_MINUS)
    place_boxes(m2)
    viewer_logger.log(m2.make_rendering().part)

    # different side and orientation, but the same placement code works as expected.
    # notice that the placed nodes have an orientation that matches the side's orientation
    m3 = Assembler.make_with_element(base, side=AxDir3.Y_MINUS)
    place_boxes(m3)
    viewer_logger.log(m3.make_rendering().part)


def test_add_features(viewer_logger: ModelLogger) -> None:
    class TestFeature(Feature):
        @override
        def desired_size(self) -> Feature.DesiredSize:
            return Feature.DesiredSize(Vec2(10, 10))
            
        @override
        def render(self, plate: Bx) -> list[Piece]:
            maker = Assembler.make(plate)
            maker_cutout = maker.make_cutout_sub()
            maker_cutout.place_element(BoxElement(10, 10, 10))
            return maker.all_pieces()
            
    base = BoxElement(50, 50, 10)
    m1 = Assembler.make_with_element(base, side=AxDir3.TOP)
    m1.add_features([[TestFeature()]])
    r1 = m1.make_rendering()
    # assert m1._pieces is not None and len(m1._pieces) == 2
    # assert m1.origin == Vec3(0, 0, 10)
    # assert m1._pieces[0].part.position == Vector(0, 0, 5)
    # assert m1._pieces[1].part.position == Vector(0, 0, 5)
    # assert r1.part.position == Vector(0, 0, 5)
    viewer_logger.log(r1.part)