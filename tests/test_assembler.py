from typing import override

import build123d as bd
import pytest

from mini_rack_printables import (
    Assembler,
    AxDir3,
    BoxBlock,
    Bx,
    Dir2,
    Feature,
    Rc,
    RowLayout,
    TestLogger,
    Vec2,
    Vec3,
)


def test_make() -> None:
    base = Bx(100, 100, 10, 0, 0, 5)

    # on the top side of the base
    m1 = Assembler.make(base)
    assert m1.origin == Vec3(0, 0, 10)
    assert m1.plate_rc == Rc(100, 100)
    assert m1.plate_depth == 10
    assert m1._plate.side == AxDir3.Z_PLUS
    assert m1._plate.plane.location.position == bd.Vector(0, 0, 10)
    assert m1._plate.z_dir == AxDir3.Z_PLUS

    # on the right side of the base pointing outward
    m2 = Assembler.make(base, z_dir=AxDir3.X_PLUS)
    assert m2.origin == Vec3(50, 0, 5)
    assert m2.plate_rc == Rc(100, 10)
    assert m2.plate_depth == 100
    assert m2._plate.side == AxDir3.X_PLUS
    assert m2._plate.plane.location.position == m2.origin.to_vector()
    assert m2._plate.z_dir == AxDir3.X_PLUS


def test_make_with_block() -> None:
    base = BoxBlock(100, 100, 10)

    m1 = Assembler.make_with_block(base)
    assert m1.origin == Vec3(0, 0, 10)
    assert m1.plate_rc == Rc(100, 100)
    assert m1.plate_depth == 10
    assert m1._plate.side == AxDir3.Z_PLUS
    assert m1._plate.plane.location.position == bd.Vector(0, 0, 10)

    # on the right side of the base pointing outward
    m2 = Assembler.make_with_block(base, z_dir=AxDir3.X_PLUS)
    assert m2.origin == Vec3(50, 0, 5)
    assert m2.plate_rc == Rc(100, 10)
    assert m2.plate_depth == 100
    assert m2._plate.side == AxDir3.X_PLUS
    assert m2._plate.plane.location.position == m2.origin.to_vector()
    assert m2.z_dir == AxDir3.X_PLUS


def test_assemble_two_boxes(viewer_logger: TestLogger) -> None:
    base = BoxBlock(30, 20, 10)

    def place_nodes(asm: Assembler) -> None:
        node = BoxBlock(2, 1.5, 1)
        # place the same node at multiple places on the assembler's plane
        add_places = [
            Assembler.Place(origin=dir2) for dir2 in [Dir2.CENTER, Dir2.CORNER_RT_TP]
        ]
        asm.place_block(node, add_places, cut=False)
        # cut out a node use the cut mode and the offset placement to render inside the base
        sub_places = [Assembler.Place(origin=Dir2.CORNER_LF_BT, offset=Vec3(0, 0, -1))]
        asm.place_block(node, sub_places, cut=True)

    # place the nodes on the base using a assembler
    m1 = Assembler.make_with_block(base, z_dir=AxDir3.TOP)
    place_nodes(m1)
    viewer_logger.log(m1.make_rendering())

    # different side and orientation, but the same placement code works as expected.
    # notice that the placed nodes have an orientation that matches the side's orientation
    m2 = Assembler.make_with_block(base, z_dir=AxDir3.Z_MINUS)
    place_nodes(m2)
    viewer_logger.log(m2.make_rendering())

    # different side and orientation, but the same placement code works as expected.
    # notice that the placed nodes have an orientation that matches the side's orientation
    m3 = Assembler.make_with_block(base, z_dir=AxDir3.Y_MINUS)
    place_nodes(m3)
    viewer_logger.log(m3.make_rendering())


def test_cutout_mode(viewer_logger: TestLogger) -> None:
    base = BoxBlock(50, 50, 10)

    # make a base
    m1 = Assembler.make_with_block(base, z_dir=AxDir3.TOP)
    assert m1.origin == Vec3(0, 0, 10)
    assert not m1.cutout_mode

    # cut out a hole
    c1 = m1.make_cutout_sub()
    assert c1.origin == Vec3(0, 0, 0)
    assert c1.plate_rc == m1.plate_rc
    assert c1.z_dir == m1.z_dir
    assert c1.cutout_mode
    with pytest.raises(RuntimeError):
        _ = c1.make_cutout_sub()
    c1.place_block(BoxBlock(10, 10, 10))

    # add a side to the base and cut a hole in it
    m2 = m1.stack_block(
        BoxBlock(10, 50, 50), Assembler.Place(origin=Dir2.SIDE_RIGHT), AxDir3.X_PLUS
    )
    assert m2.origin == Vec3(25, 0, 35)
    c2 = m2.make_cutout_sub()
    assert c2.origin == Vec3(15, 0, 35)
    c2.place_block(BoxBlock(10, 10, 10))

    # add a top plate with a hole in it
    m2_top = m2.make_sub(
        z_dir=AxDir3.Z_PLUS
    )  # m2 uses the X_PLUS side, for the stack we want the Z_PLUS
    m3 = m2_top.stack_block(
        BoxBlock(50, 50, 10), Assembler.Place(origin=Dir2.SIDE_RIGHT)
    )
    c3 = m3.make_cutout_sub()
    c3.place_block(BoxBlock(10, 10, 10))

    r1 = m1.make_rendering()
    viewer_logger.log(r1.part)


class TestFeature(Feature):
    @override
    def desired_size(self) -> Feature.DesiredSize:
        return Feature.DesiredSize(Vec2(10, 10))

    @override
    def render(self, asm: Assembler) -> None:
        cutout_asm = asm.make_cutout_sub()
        cutout_asm.place_block(BoxBlock(10, 10, 10))


def test_add_feature(viewer_logger: TestLogger) -> None:
    base = BoxBlock(50, 50, 10)
    m1 = Assembler.make_with_block(base, z_dir=AxDir3.TOP)
    tf = TestFeature()
    tf.render(m1)
    r1 = m1.make_rendering()
    assert m1._pieces is not None and len(m1._pieces) == 2
    assert m1.origin == Vec3(0, 0, 10)
    assert m1._pieces[0]._bbox.center() == bd.Vector(0, 0, 5)
    assert m1._pieces[1]._bbox.center() == bd.Vector(0, 0, 5)
    viewer_logger.log(r1.part)


def test_add_feature_twice(viewer_logger: TestLogger) -> None:
    # Create a L shaped base out of two boxes stacked
    top_asm = Assembler.make_with_block(BoxBlock(50, 50, 10), z_dir=AxDir3.TOP)
    side_asm = top_asm.stack_block(
        BoxBlock(10, 50, 50), Assembler.Place(origin=Dir2.X_PLUS), AxDir3.X_PLUS
    )

    # Use the test feature to cut holes into the base
    tf = TestFeature()
    tf.render(top_asm)
    tf.render(side_asm)
    r1 = top_asm.make_rendering()
    viewer_logger.log(r1.part)
