from mini_rack_printables import (
    Div,
    Rc,
    ModelPart,
    PartPiece,
    Selector,
    Plate,
)
from build123d import Vector, Axis


def test_extend_sizes():
    assert Div.extend_sizes([10, "*"], 4) == [10, "*", "*", "*"]
    assert Div.extend_sizes([10, 20], 2) == [10, 20]


def test_is_valid_sizes():
    assert Div.is_valid_sizes(["*", 3.5, 4, 9])
    assert not Div.is_valid_sizes([3.0, 0, -1])
    assert not Div.is_valid_sizes(["-"])


def test_sizes_operations():
    sizes1 = ["*"]
    assert Div.count_auto(sizes1) == 1
    assert Div.sum_static(sizes1) == 0

    sizes2 = ["*", "*"]
    assert Div.count_auto(sizes2) == 2
    assert Div.sum_static(sizes2) == 0

    sizes3 = ["*", 100, "*"]
    assert Div.count_auto(sizes3) == 2
    assert Div.sum_static(sizes3) == 100

    sizes4 = ["*", 100, 50.3, "*"]
    assert Div.count_auto(sizes4) == 2
    assert Div.sum_static(sizes4) == 150.3


def test_fill_in_sizes():
    sizes1 = ["*", 100, "*"]
    result1 = Div.fill_in_sizes(sizes1, Vector(200, 200))
    assert result1 == [50, 100, 50]

    result2 = Div.fill_in_sizes(sizes1, Vector(200, 200), Axis.Y)
    assert result2 == [50, 100, 50]

    sizes4 = ["*", 100, 40.0, "*"]
    result4 = Div.fill_in_sizes(sizes4, Vector(200, 200))
    assert result4 == [30, 100, 40.0, 30]


def test_divide_equally():
    r1 = Rc([2, 2])
    divisions1 = Div.divide_by_sizes(r=r1, sizes=["*"])
    assert divisions1[0] == r1

    r2 = Rc([4, 2])
    divisions2 = Div.divide_by_sizes(r=r2, sizes=["*", "*"])
    assert divisions2 == [Rc((2, 2), (-1, 0)), Rc((2, 2), (1, 0))]

    r3 = Rc([6, 1])
    divisions3 = Div.divide_by_sizes(r=r3, sizes=["*", "*", "*"])
    assert divisions3 == [Rc((2, 1), (-2, 0)), Rc((2, 1), (0, 0)), Rc((2, 1), (2, 0))]


def test_divide_horizontally():
    r1 = Rc([2, 2])
    divisions1 = Div.divide_by_sizes(r=r1, sizes=[1])
    assert divisions1[0] == r1

    r2 = Rc([4, 2])
    divisions2 = Div.divide_by_sizes(r=r2, sizes=[1, "*"])
    assert len(divisions2) == 2
    assert divisions2[0] == Rc([1, 2], [-1.5, 0])
    assert divisions2[1] == Rc([3, 2], [0.5, 0])

    r3 = Rc([6, 1])
    divisions3 = Div.divide_by_sizes(r=r3, sizes=[1, "*", 1])
    assert len(divisions3) == 3
    assert divisions3[0] == Rc([1, 1], [-2.5, 0])
    assert divisions3[1] == Rc([4, 1], [0, 0])
    assert divisions3[2] == Rc([1, 1], [2.5, 0])


def test_divide_vertically():
    r2 = Rc([2, 4])
    divisions2 = Div.divide_by_sizes(r=r2, sizes=[1, "*"], axis=Axis.Y)
    assert len(divisions2) == 2
    assert divisions2[0] == Rc([2, 1], [0, -1.5])
    assert divisions2[1] == Rc([2, 3], [0, 0.5])

    r3 = Rc([1, 6])
    divisions3 = Div.divide_by_sizes(r=r3, sizes=[1, "*", 1], axis=Axis.Y)
    assert len(divisions3) == 3
    assert divisions3[0] == Rc([1, 1], [0, -2.5])
    assert divisions3[1] == Rc([1, 4], [0, 0])
    assert divisions3[2] == Rc([1, 1], [0, 2.5])


class DummyPart(ModelPart):
    _layout_size: Vector

    def __init__(
        self,
        align: Selector = Selector.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0.0,
        layout_size: Vector = Vector(0, 0),
    ):
        super().__init__(align, shift, padding)
        self._layout_size = layout_size

    def layout_size(self, plate_size: Vector) -> Vector:
        return self._layout_size

    def render(self, plate: Plate) -> list[PartPiece]:
        return []


def test_layout_part():
    centerAligned = DummyPart(align=Selector.CENTER, layout_size=Vector(10, 10))
    assert Div.layout_part(centerAligned, Rc((100, 100))) == Vector(0, 0)

    leftAligned = DummyPart(align=Selector.LEFT, layout_size=Vector(10, 10))
    assert Div.layout_part(leftAligned, Rc((100, 100))) == Vector(-45, 0)

    leftAlignedPadded = DummyPart(align=Selector.LEFT, padding=1, layout_size=Vector(10, 10))
    assert Div.layout_part(leftAlignedPadded, Rc((100, 100))) == Vector(-44, 0)

    leftAlignedShifted = DummyPart(
        align=Selector.LEFT, shift=Vector(10, 0), layout_size=Vector(10, 10)
    )
    assert Div.layout_part(leftAlignedShifted, Rc((100, 100))) == Vector(-35, 0)

    leftBottom = DummyPart(
        align=Selector.BOTTOM_LEFT, layout_size=Vector(10, 10)
    )
    assert Div.layout_part(leftBottom, Rc((100, 100), (10, 10))) == Vector(-35, -35)
