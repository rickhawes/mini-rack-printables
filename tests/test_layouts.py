from mini_rack_printables import (
    RowColumnCollection,
    MeasuredRowsColumns,
    ModelPart,
    Spacer,
    RowLayout,
    GridLayout,
    PlatePlanes,
    Bx,
    Place,
)
from build123d import Rectangle, Sketch, Circle, Location
import pytest

ALIGN_CELL = "Align cell tests"
SINGLE_ROW = "single row tests"
ROW_LAYOUT = "row layout tests"
GRID_LAYOUT = "grid layout tests"


def test_measured_rows_columns():
    p1 = Spacer(10, 5)
    p2 = Spacer(20, 15)
    p3 = Spacer(30, 25)
    e4 = Spacer(10, 5, more_x=True)
    e5 = Spacer(10, 5, more_y=True)

    coll = RowColumnCollection[ModelPart]([[p1, p2, p3], [p1, p2, p3], [p1, p2, p3]])
    m1 = MeasuredRowsColumns.measure_parts(coll)
    assert m1.min_x == [10, 20, 30]
    assert m1.min_y == [25, 25, 25]
    assert m1.more_x == [False, False, False]
    assert m1.more_y == [False, False, False]

    coll2 = RowColumnCollection[ModelPart]([[e4, p2, p3], [p1, p2, p3], [p1, p2, p3]])
    m2 = MeasuredRowsColumns.measure_parts(coll2)
    assert m2.min_x == [10, 20, 30]
    assert m2.min_y == [25, 25, 25]
    assert m2.more_x == [True, False, False]
    assert m2.more_y == [False, False, False]

    coll3 = RowColumnCollection[ModelPart]([[p1, p2, p3], [p2, p2, p3], [e5, p2, p3]])
    m3 = MeasuredRowsColumns.measure_parts(coll3)
    assert m3.min_x == [20, 20, 30]
    assert m3.min_y == [25, 25, 25]
    assert m3.more_x == [False, False, False]
    assert m3.more_y == [False, False, True]


def sketch_sub_plates(sub_plates: list[PlatePlanes]) -> Sketch:
    sk = Sketch()
    for p in sub_plates:
        b = p.bounds
        sk += p.bottom_plane * Location(b.shift) * Rectangle(b.size.X, b.size.Y)
        sk -= p.bottom_plane * Circle(0.2)
    return Sketch(sk)


def test_row_heights_values():
    p1 = Spacer(10, 10)
    p2 = Spacer(15, 15)
    p3 = Spacer(20, 20)

    with pytest.raises(ValueError):
        _ = RowLayout(equal_heights=True, row_heights=[2, 3], spacing=2)

    with pytest.raises(ValueError):
        l1 = RowLayout(row_heights=[10], spacing=2)
        _ = l1.layout_parts([[p1], [p2, p3]], PlatePlanes(Bx((60, 20, 0))))

    with pytest.raises(ValueError):
        l2 = RowLayout(row_heights=[10, 40], spacing=2)
        _ = l2.layout_parts([[p1], [p2, p3]], PlatePlanes(Bx((60, 20, 0))))

    l3 = RowLayout(row_heights=[10, 40], spacing=2)
    _ = l3.layout_parts([[p1], [p2, p3]], PlatePlanes(Bx((60, 56, 0))))


def test_too_large_widths():
    with pytest.raises(ValueError):
        p1 = Spacer(10, 10)
        p2 = Spacer(15, 15)
        p3 = Spacer(20, 20)

        layout = RowLayout(equal_widths=True, spacing=2)
        plate = PlatePlanes(Bx((30, 30, 0)))  # too small of a plate for theses parts
        _ = layout.layout_parts([p1, p2, p3], plate)


def test_too_large_height():
    with pytest.raises(ValueError):
        p1 = Spacer(10, 10)
        p2 = Spacer(15, 15)
        p3 = Spacer(20, 20)

        layout = RowLayout(equal_widths=True, spacing=2)
        plate = PlatePlanes(Bx((60, 20, 0)))  # too small of a plate for theses parts
        _ = layout.layout_parts([p1, p2, p3], plate)


def test_align_cell(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(15, 15)
    plate = PlatePlanes(Bx((40, 40, 0)))

    l1 = RowLayout(align=Place.CENTER, spacing=2)
    sub_plates = l1.layout_parts([p1, p2], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), ALIGN_CELL)

    l2 = RowLayout(align=Place.LEFT, spacing=2)
    sub_plates = l2.layout_parts([p1, p2], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), ALIGN_CELL)

    l3 = RowLayout(align=Place.TOP, spacing=2)
    sub_plates = l3.layout_parts([p1, p2], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), ALIGN_CELL)

    l4 = RowLayout(align=Place.BOTTOM_RIGHT, spacing=2)
    sub_plates = l4.layout_parts([p1, p2], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), ALIGN_CELL)


def test_even_col_layout(viewer_logger):
    p1 = Spacer(10, 10)
    p2 = Spacer(15, 15)
    p3 = Spacer(20, 20)

    layout = RowLayout(equal_widths=True, spacing=2)
    plate = PlatePlanes(Bx((60, 30, 0)))
    sub_plates = layout.layout_parts([p1, p2, p3], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), SINGLE_ROW)


def test_proportional_col_layout(viewer_logger):
    p1 = Spacer(10, 10)
    p2 = Spacer(15, 15)
    p3 = Spacer(20, 20)

    layout = RowLayout(spacing=2)
    plate = PlatePlanes(Bx((60, 30, 0)))
    sub_plates = layout.layout_parts([p1, p2, p3], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), SINGLE_ROW)


def test_expand_col_layout(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15, more_x=True)

    layout = RowLayout(spacing=2)
    plate = PlatePlanes(Bx((60, 30, 0)))
    sub_plates = layout.layout_parts([p1, p2, p3], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), SINGLE_ROW)


def test_expand_two_col_layout(viewer_logger):
    p1 = Spacer(5, 5, more_x=True)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15, more_x=True)

    layout = RowLayout(spacing=2)
    plate = PlatePlanes(Bx((60, 30, 0)))
    sub_plates = layout.layout_parts([p1, p2, p3], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), SINGLE_ROW)


def test_proportional_layout(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(spacing=2)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), ROW_LAYOUT)


def test_equal_cols_layout(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(equal_widths=True, spacing=2)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), ROW_LAYOUT)


def test_equal_rows_layout(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(equal_heights=True, spacing=2)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), ROW_LAYOUT)


def test_equal_rows_cols_layout(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(equal_heights=True, equal_widths=True, spacing=2)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), ROW_LAYOUT)


def test_expanding_cols_layout(viewer_logger):
    p1 = Spacer(5, 5)
    e1 = Spacer(5, 5, more_x=True)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)
    e3 = Spacer(15, 15, more_x=True)

    layout = RowLayout(spacing=2)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[e1, p2, p3], [p1, p2, e3]], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), ROW_LAYOUT)


def test_expanding_row_layout(viewer_logger):
    p1 = Spacer(5, 5)
    e1 = Spacer(5, 5, more_y=True)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(spacing=2)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[e1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), ROW_LAYOUT)


def test_explict_row_heights(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)
    e3 = Spacer(15, 15, more_x=True)

    layout = RowLayout(row_heights=[14, 44], spacing=(2 / 3))
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3], [p1, p2, e3]], plate)

    viewer_logger.log(sketch_sub_plates(sub_plates), ROW_LAYOUT)


def test_one_row_grid(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3]], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), GRID_LAYOUT)


def test_one_equal_row_grid(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, equal_widths=True)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3]], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), GRID_LAYOUT)


def test_one_specified_row_grid(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, col_widths=[5, 20, 15])
    plate = PlatePlanes(Bx((48, 30, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3]], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), GRID_LAYOUT)


def test_one_expanded_row_grid(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10, more_x=True)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, col_widths=[5, 20, 15])
    plate = PlatePlanes(Bx((48, 30, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3]], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), GRID_LAYOUT)


def test_sparse_grid(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3], [p1, p2], [p1]], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), GRID_LAYOUT)


def test_sparse_equal_row_grid(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, equal_heights=True)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3], [p1, p2], [p1]], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), GRID_LAYOUT)


def test_sparse_equal_grid(viewer_logger):
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, equal_widths=True, equal_heights=True)
    plate = PlatePlanes(Bx((60, 60, 0)))
    sub_plates = layout.layout_parts([[p1, p2, p3], [p1, p2], [p1]], plate)
    viewer_logger.log(sketch_sub_plates(sub_plates), GRID_LAYOUT)
