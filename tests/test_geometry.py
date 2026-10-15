from mini_rack_printables import Rc, Place, Vec2, Vec3, Ax, Bx, AxAlign, AxDir
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


def test_place_center():
    other_rc = Rc.from_values(10, 10)
    rc = Rc.from_values(2, 2)

    center_left = rc.place_center(other_rc, Place.LEFT_SIDE)
    assert center_left == Vec2(-4, 0)
    center_top = rc.place_center(other_rc, Place.TOP_SIDE)
    assert center_top == Vec2(0, 4)
    center_top_left = rc.place_center(other_rc, Place.TOP_LEFT)
    assert center_top_left == Vec2(-4, 4)

    other_rc2 = Rc.from_values(10, 10, 20, 20)
    center_left2 = rc.place_center(other_rc2, Place.LEFT_SIDE)
    assert center_left2 == Vec2(16, 20)
    center_top_left2 = rc.place_center(other_rc2, Place.TOP_LEFT)
    assert center_top_left2 == Vec2(16, 24)


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
    l1 = Rc.arrange(AxAlign.X, rc1, rc2)
    assert l1[0] == Rc.from_values(4, 4, -1, 0)
    assert l1[1] == Rc.from_values(2, 2, 2, 0)
    l2 = Rc.arrange(AxAlign.X_BOTTOM, rc1, rc2)
    assert l2[0] == Rc.from_values(4, 4, -1, 0)
    assert l2[1] == Rc.from_values(2, 2, 2, -1)
    l3 = Rc.arrange(AxAlign.X_TOP, rc1, rc2)
    assert l3[0] == Rc.from_values(4, 4, -1, 0)
    assert l3[1] == Rc.from_values(2, 2, 2, 1)
    l4 = Rc.arrange(AxAlign.X_BOTTOM, rc1, rc2, rc3)
    assert l4[0] == Rc.from_values(4, 4, -2, 0)
    assert l4[1] == Rc.from_values(2, 2, 1, -1)
    assert l4[2] == Rc.from_values(2, 4, 3, 0)
    l5 = Rc.arrange(AxAlign.X, rc1)
    assert l5[0] == Rc.from_values(4, 4, 0, 0)
    l6 = Rc.arrange(AxAlign.X)
    assert len(l6) == 0


def test_arrange_vertical():
    rc1 = Rc.from_values(4, 4)
    rc2 = Rc.from_values(2, 2)
    rc3 = Rc.from_values(4, 2)
    l1 = Rc.arrange(AxAlign.Y, rc1, rc2)
    assert l1[0] == Rc.from_values(4, 4, 0, -1)
    assert l1[1] == Rc.from_values(2, 2, 0, 2)
    l2 = Rc.arrange(AxAlign.Y_LEFT, rc1, rc2, rc3)
    assert l2[0] == Rc.from_values(4, 4, 0, -2)
    assert l2[1] == Rc.from_values(2, 2, -1, 1)
    assert l2[2] == Rc.from_values(4, 2, 0, 3)
    l5 = Rc.arrange(AxAlign.Y_RIGHT, rc1)
    assert l5[0] == Rc.from_values(4, 4, 0, 0)


def test_bx_init():
    with pytest.raises(ValueError):
        _ = Bx(Vec3(-1, -1, 1))

    bx1 = Bx(size=Vec3(1, 1, 1))
    assert bx1.size == Vec3(1, 1, 1)
    assert bx1.center == Vec3(0, 0, 0)

    bx3 = Bx.from_values(dx=3, dy=3, dz=1, x=-1, y=-1, z=-1)
    assert bx3.size == Vec3(3, 3, 1)


def test_bx_props():
    bx = Bx.from_values(4, 6, 3, 1, 1, 1)
    assert bx.size == Vec3(4, 6, 3)
    assert bx.center == Vec3(1, 1, 1)
    assert bx.back == 4
    assert bx.front == -2
    assert bx.left == -1
    assert bx.right == 3
    assert bx.bottom == -0.5
    assert bx.top == 2.5


def test_bx_shift():
    bx = Bx.from_values(4, 6, 3, 1, 1, 1)
    assert bx.size == Vec3(4, 6, 3)
    assert bx.center == Vec3(1, 1, 1)

    bx2 = bx.move(Vec3(-1, -1, -1))
    assert bx2.size == Vec3(4, 6, 3)
    assert bx2.center == Vec3(0, 0, 0)


def test_bx_side_center():
    bx = Bx(size=Vec3(4, 8, 6), center=Vec3(1, 1, 1))
    assert bx.side_center(AxDir.TOP) == Vec3(1, 1, 4)
    assert bx.side_center(AxDir.BOTTOM) == Vec3(1, 1, -2)
    assert bx.side_center(AxDir.LEFT) == Vec3(-1, 1, 1)
    assert bx.side_center(AxDir.RIGHT) == Vec3(3, 1, 1)
    assert bx.side_center(AxDir.PLUS_Y) == Vec3(1, 5, 1)
    assert bx.side_center(AxDir.MINUS_Y) == Vec3(1, -3, 1)


def test_bx_side_size():
    bx = Bx(size=Vec3(4, 8, 6), center=Vec3(1, 1, 1))
    assert bx.side_size(AxDir.TOP) == Vec2(4, 8)
    assert bx.side_size(AxDir.BOTTOM) == Vec2(4, 8)
    assert bx.side_size(AxDir.LEFT) == Vec2(8, 6)
    assert bx.side_size(AxDir.RIGHT) == Vec2(8, 6)
    assert bx.side_size(AxDir.PLUS_Y) == Vec2(4, 6)
    assert bx.side_size(AxDir.MINUS_Y) == Vec2(4, 6)
