from mini_rack_printables import Rc, Place, Vec2, Vec3, Ax, Bx
import pytest


def test_init():
    with pytest.raises(ValueError):
        _ = Rc.from_values(-1, -1)

    rc1 = Rc(Vec2(1, 1))
    assert rc1.size == Vec2(1, 1)
    assert rc1.center == Vec2(0, 0)

    rc2 = Rc(Vec2(2, 2))
    assert rc2.size == Vec2(2, 2)

    rc3 = Rc.from_values(dx=3, dy=3, x=-1, y=-1)
    assert rc3.size.x == 3
    assert rc3.size.y == 3


def test_edge_functions():
    rc = Rc.from_values(4, 6, 1, 1)

    assert rc.left == -1
    assert rc.right == 3
    assert rc.top == 4
    assert rc.bottom == -2
    assert rc.min == Vec2(-1, -2)
    assert rc.max == Vec2(3, 4)


def test_from_edges():
    rc1 = Rc.from_values(4, 6, 1, 1)
    rc2 = Rc.from_edges(left=rc1.left, right=rc1.right, bottom=rc1.bottom, top=rc1.top)
    assert rc1 == rc2


def test_apply_padding():
    rc1 = Rc.from_values(4, 6, 1, 1)
    rc2 = rc1.apply_padding(1)
    assert rc2 == Rc(Vec2(6, 8), Vec2(1, 1))


def test_zero_rc_apply_padding():
    rc1 = Rc(Vec2(0, 0))
    rc2 = rc1.apply_padding(4)
    assert rc2 == Rc.from_values(8, 8)


def test_apply_zero_padding():
    rc1 = Rc.from_values(4, 6, 1, 1)
    rc2 = rc1.apply_padding(0)
    assert rc2 == rc1


def test_union():
    rc1 = Rc.from_values(4, 6, 1, 1)
    rc2 = Rc.from_values(4, 6, -1, -1)
    rc3 = Rc.union(rc1, rc2)
    assert rc3 == Rc(Vec2(6, 8))


def test_centered_bounding():
    rc1 = Rc.from_values(4, 6, 1, 1)
    rc2 = rc1.centered_bounding()
    assert rc2 == Rc.from_values(6, 8)

    rc3 = Rc.from_values(4, 6, -1, -1)
    rc4 = rc3.centered_bounding()
    assert rc4 == Rc.from_values(6, 8)


def test_alignment_shift():
    bounding_rc = Rc.from_values(10, 10)
    rc = Rc.from_values(2, 2)

    shift_left = rc.bounds_shift(bounding_rc, Place.LEFT_EDGE)
    assert shift_left == Vec2(-4, 0)
    shift_top = rc.bounds_shift(bounding_rc, Place.TOP_EDGE)
    assert shift_top == Vec2(0, 4)
    shift_top_left = rc.bounds_shift(bounding_rc, Place.TOP_LEFT)
    assert shift_top_left == Vec2(-4, 4)

    bounding_rc2 = Rc.from_values(10, 10, 20, 20)
    shift_left2 = rc.bounds_shift(bounding_rc2, Place.LEFT_EDGE)
    assert shift_left2 == Vec2(16, 20)
    shift_top_left2 = rc.bounds_shift(bounding_rc2, Place.TOP_LEFT)
    assert shift_top_left2 == Vec2(16, 24)


def test_split():
    rc = Rc.from_values(8, 8, 4, 4)

    split1 = rc.split(amount=1, along=Ax.X)
    assert split1 == [Rc(Vec2(1, 8), Vec2(0.5, 4)), Rc(Vec2(7, 8), Vec2(4.5, 4))]

    split2 = rc.split(amount=-2, along=Ax.X)
    assert split2 == [Rc(Vec2(6, 8), Vec2(3, 4)), Rc(Vec2(2, 8), Vec2(7, 4))]

    split3 = rc.split(amount=1, along=Ax.Y)
    assert split3 == [Rc(Vec2(8, 1), Vec2(4, 0.5)), Rc(Vec2(8, 7), Vec2(4, 4.5))]

    split4 = rc.split(amount=-2, along=Ax.Y)
    assert split4 == [Rc(Vec2(8, 6), Vec2(4, 3)), Rc(Vec2(8, 2), Vec2(4, 7))]


def test_arrange_horizontal():
    rc1 = Rc.from_values(4, 4)
    rc2 = Rc.from_values(2, 2)
    rc3 = Rc.from_values(2, 4)
    l1 = Rc.arrange(Ax.X, Place.CENTER, rc1, rc2)
    assert l1[0] == Rc.from_values(4, 4, -1, 0)
    assert l1[1] == Rc.from_values(2, 2, 2, 0)
    l2 = Rc.arrange(Ax.X, Place.BOTTOM_EDGE, rc1, rc2)
    assert l2[0] == Rc.from_values(4, 4, -1, 0)
    assert l2[1] == Rc.from_values(2, 2, 2, -1)
    l3 = Rc.arrange(Ax.X, Place.TOP_EDGE, rc1, rc2)
    assert l3[0] == Rc.from_values(4, 4, -1, 0)
    assert l3[1] == Rc.from_values(2, 2, 2, 1)
    l4 = Rc.arrange(Ax.X, Place.BOTTOM_EDGE, rc1, rc2, rc3)
    assert l4[0] == Rc.from_values(4, 4, -2, 0)
    assert l4[1] == Rc.from_values(2, 2, 1, -1)
    assert l4[2] == Rc.from_values(2, 4, 3, 0)
    l5 = Rc.arrange(Ax.X, Place.CENTER, rc1)
    assert l5[0] == Rc.from_values(4, 4, 0, 0)
    l6 = Rc.arrange(Ax.X, Place.CENTER)
    assert len(l6) == 0


def test_arrange_vertical():
    rc1 = Rc.from_values(4, 4)
    rc2 = Rc.from_values(2, 2)
    rc3 = Rc.from_values(4, 2)
    l1 = Rc.arrange(Ax.Y, Place.CENTER, rc1, rc2)
    assert l1[0] == Rc.from_values(4, 4, 0, -1)
    assert l1[1] == Rc.from_values(2, 2, 0, 2)
    l2 = Rc.arrange(Ax.Y, Place.LEFT_EDGE, rc1, rc2, rc3)
    assert l2[0] == Rc.from_values(4, 4, 0, -2)
    assert l2[1] == Rc.from_values(2, 2, -1, 1)
    assert l2[2] == Rc.from_values(4, 2, 0, 3)
    l5 = Rc.arrange(Ax.Y, Place.RIGHT_EDGE, rc1)
    assert l5[0] == Rc.from_values(4, 4, 0, 0)


def test_bx_init():
    with pytest.raises(ValueError):
        _ = Bx(-1, -1, 1)

    bx1 = Bx(size=Vec3(1, 1, 1))
    assert bx1.size == Vec3(1, 1, 1)
    assert bx1.center == Vec3(0, 0, 0)

    bx2 = Bx(Vec3(2, 2, 3))
    assert bx2.size == Vec3(2, 2, 3)

    bx3 = Bx(dx=3, dy=3, dz=1, x=-1, y=-1, z=-1)
    assert bx3.size == Vec3(3, 3, 1)

    bx4 = Bx(bx3)
    assert bx4.center == Vec3(-1, -1, -1)


def test_bx_props():
    bx = Bx(4, 6, 3, 1, 1, 1)
    assert bx.size == Vec3(4, 6, 3)
    assert bx.center == Vec3(1, 1, 1)
    assert bx.top == 4
    assert bx.bottom == -2
    assert bx.left == -1
    assert bx.right == 3
    assert bx.front == -0.5
    assert bx.back == 2.5


def test_bx_shift():
    bx = Bx(4, 6, 3, 1, 1, 1)
    assert bx.size == Vec3(4, 6, 3)
    assert bx.center == Vec3(1, 1, 1)

    bx2 = bx.move(Vec3(-1, -1, -1))
    assert bx2.size == Vec3(4, 6, 3)
    assert bx2.center == Vec3(0, 0, 0)
