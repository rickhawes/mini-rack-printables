from mini_rack_printables import Rc, RcAlignment, Dir
from build123d import Vector


def test_edge_functions():
    rc = Rc((4, 6), shift=(1, 1))

    assert rc.left == -1
    assert rc.right == 3
    assert rc.top == 4
    assert rc.bottom == -2


def test_from_edges():
    rc1 = Rc((4, 6), (1, 1))
    rc2 = Rc.from_edges(left=rc1.left, right=rc1.right, bottom=rc1.bottom, top=rc1.top)
    assert rc1 == rc2


def test_divide_horizontally():
    rc1 = Rc((4, 6))
    div1 = rc1.divide(2)
    assert div1[0] == Rc((2, 6), (-1, 0))
    assert div1[1] == Rc(size=(2, 6), shift=(1, 0))

    rc2 = Rc((4, 6))
    div2 = rc2.divide(1)
    assert div2[0] == rc2

    rc3 = Rc((6, 6))
    div3 = rc3.divide(3)
    assert div3[0] == Rc((2, 6), (-2, 0))
    assert div3[1] == Rc(size=(2, 6), shift=(0, 0))
    assert div3[2] == Rc(size=(2, 6), shift=(2, 0))


def test_apply_padding():
    rc1 = Rc((4, 6), (1, 1))
    rc2 = rc1.apply_padding(1)
    assert rc2 == Rc((6, 8), (1, 1))


def test_zero_rc_apply_padding():
    rc1 = Rc((0, 0))
    rc2 = rc1.apply_padding(4)
    assert rc2 == Rc((8, 8))


def test_apply_zero_padding():
    rc1 = Rc((4, 6), (1, 1))
    rc2 = rc1.apply_padding(0)
    assert rc2 == rc1


def test_union():
    rc1 = Rc((4, 6), (1, 1))
    rc2 = Rc((4, 6), (-1, -1))
    rc3 = Rc.union(rc1, rc2)
    assert rc3 == Rc((6, 8))


def test_centered_bounding():
    rc1 = Rc((4, 6), (1, 1))
    rc2 = rc1.centered_bounding()
    assert rc2 == Rc((6, 8), (0, 0))

    rc3 = Rc((4, 6), (-1, -1))
    rc4 = rc3.centered_bounding()
    assert rc4 == Rc((6, 8), (0, 0))


def test_alignment_shift():
    bounding_rc = Rc((10, 10))
    rc = Rc((2, 2))

    shift_left = rc.alignment_shift(bounding_rc, RcAlignment.LEFT)
    assert shift_left == Vector(-4, 0)
    shift_top = rc.alignment_shift(bounding_rc, RcAlignment.TOP)
    assert shift_top == Vector(0, 4)
    shift_top_left = rc.alignment_shift(bounding_rc, RcAlignment.TOP + RcAlignment.LEFT)
    assert shift_top_left == Vector(-4, 4)

    bounding_rc2 = Rc((10, 10), (20, 20))
    shift_left2 = rc.alignment_shift(bounding_rc2, RcAlignment.LEFT)
    assert shift_left2 == Vector(16, 20)
    shift_top_left2 = rc.alignment_shift(
        bounding_rc2, RcAlignment.TOP + RcAlignment.LEFT
    )
    assert shift_top_left2 == Vector(16, 24)


def test_split():
    rc = Rc((8, 8), (4, 4))

    split1 = rc.split(amount=1, dir=Dir.HORIZONTAL)
    assert split1 == [Rc((1, 8), (0.5, 4)), Rc((7, 8), (4.5, 4))]

    split2 = rc.split(amount=-2, dir=Dir.HORIZONTAL)
    assert split2 == [Rc((6, 8), (3, 4)), Rc((2, 8), (7, 4))]

    split3 = rc.split(amount=1, dir=Dir.VERTICAL)
    assert split3 == [Rc((8, 1), (4, 0.5)), Rc((8, 7), (4, 4.5))]

    split4 = rc.split(amount=-2, dir=Dir.VERTICAL)
    assert split4 == [Rc((8, 6), (4, 3)), Rc((8, 2), (4, 7))]
