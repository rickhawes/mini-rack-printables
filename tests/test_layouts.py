from collections.abc import Sequence

import pytest
from build123d import Circle, Location, Rectangle, Sketch

from mini_rack_printables import (
    Dir2,
    Feature,
    GridLayout,
    Layout,
    MeasuredRowsColumns,
    ModelLogger,
    Rc,
    RowColumnCollection,
    RowLayout,
    Spacer,
    Vec2,
)

ALIGN_CELL = "Align cell tests"
SINGLE_ROW = "single row tests"
ROW_LAYOUT = "row layout tests"
GRID_LAYOUT = "grid layout tests"


def test_measured_rows_columns() -> None:
    p1 = Spacer(10, 5)
    p2 = Spacer(20, 15)
    p3 = Spacer(30, 25)
    e4 = Spacer(10, 5, more_x=True)
    e5 = Spacer(10, 5, more_y=True)

    coll1 = RowColumnCollection[Feature]([[p1, p2, p3], [p1, p2, p3], [p1, p2, p3]])
    m1 = MeasuredRowsColumns.measure_parts(coll1)
    assert m1.min_x == [10, 20, 30]
    assert m1.min_y == [25, 25, 25]
    assert m1.more_x == [False, False, False]
    assert m1.more_y == [False, False, False]

    coll2 = RowColumnCollection[Feature]([[e4, p2, p3], [p1, p2, p3], [p1, p2, p3]])
    m2 = MeasuredRowsColumns.measure_parts(coll2)
    assert m2.min_x == [10, 20, 30]
    assert m2.min_y == [25, 25, 25]
    assert m2.more_x == [True, False, False]
    assert m2.more_y == [False, False, False]

    coll3 = RowColumnCollection[Feature]([[p1, p2, p3], [p2, p2, p3], [e5, p2, p3]])
    m3 = MeasuredRowsColumns.measure_parts(coll3)
    assert m3.min_x == [20, 20, 30]
    assert m3.min_y == [25, 25, 25]
    assert m3.more_x == [False, False, False]
    assert m3.more_y == [False, False, True]


def sketch_sections(sections: Sequence[Layout.Section]) -> Sketch:
    return Sketch(
        [
            (
                Location(s.bounds.center.to_vector()) * Rectangle(s.bounds.size.x, s.bounds.size.y)
                - Location(s.origin.to_vector()) * Circle(0.2)
            )
            for s in sections
        ]
    )


def test_row_heights_values() -> None:
    p1 = Spacer(10, 10)
    p2 = Spacer(15, 15)
    p3 = Spacer(20, 20)

    # equal_height and specified heights at the same time
    with pytest.raises(ValueError):
        _ = RowLayout(equal_heights=True, row_heights=[2, 3], spacing=2)

    # Specified row count is less than the number of rows
    with pytest.raises(ValueError):
        l1 = RowLayout(row_heights=[10], spacing=2)
        _ = l1.layout_features([[p1], [p2, p3]], Rc(60, 20))

    # Specified heights is more than plate size
    with pytest.raises(ValueError):
        l2 = RowLayout(row_heights=[10, 40], spacing=2)
        _ = l2.layout_features([[p1], [p2, p3]], Rc(60, 20))

    # specified height should be right
    l3 = RowLayout(row_heights=[10, 40], spacing=2)
    _ = l3.layout_features([[p1], [p2, p3]], Rc(60, 56))


def test_too_large_widths() -> None:
    with pytest.raises(ValueError):
        p1 = Spacer(10, 10)
        p2 = Spacer(15, 15)
        p3 = Spacer(20, 20)

        layout = RowLayout(equal_widths=True, spacing=2)
        _ = layout.layout_features([[p1, p2, p3]], Rc(30, 30))


def test_too_large_height() -> None:
    with pytest.raises(ValueError):
        p1 = Spacer(10, 10)
        p2 = Spacer(15, 15)
        p3 = Spacer(20, 20)

        layout = RowLayout(equal_widths=True, spacing=2)
        plate = Rc(60, 20)  # too small of a plate for the parts
        _ = layout.layout_features([[p1, p2, p3]], plate)


def test_equal_widths() -> None:
    p1 = Spacer(10, 10)
    p2 = Spacer(15, 15)
    p3 = Spacer(20, 20)

    layout = RowLayout(equal_widths=True, spacing=0)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3]], plate)
    assert len(sections) == 3
    assert sections[0].bounds == Rc(20, 60, -20, 0)
    assert sections[1].bounds == Rc(20, 60, 0, 0)
    assert sections[2].bounds == Rc(20, 60, 20, 0)


def test_align_cell(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(15, 15)
    plate = Rc(40, 40)

    l1: RowLayout = RowLayout(place=Dir2.CENTER, spacing=2)
    sections = l1.layout_features([[p1, p2]], plate)
    assert sections[0].bounds == Rc(12, 36, -12, 0)
    assert sections[1].bounds == Rc(22, 36, 7, 0)
    assert sections[0].origin == Vec2(-12, 0)
    assert sections[1].origin == Vec2(7, 0)
    viewer_logger.log(sketch_sections(sections), ALIGN_CELL)

    l2 = RowLayout(place=Dir2.SIDE_TOP, spacing=2)
    sections = l2.layout_features([[p1, p2]], plate)
    assert sections[0].bounds == Rc(12, 36, -12, 0)
    assert sections[1].bounds == Rc(22, 36, 7, 0)
    assert sections[0].origin == Vec2(-12, 15.5)
    assert sections[1].origin == Vec2(7, 10.5)
    viewer_logger.log(sketch_sections(sections), ALIGN_CELL)

    l3 = RowLayout(place=Dir2.SIDE_LEFT, spacing=2)
    sections = l3.layout_features([[p1, p2]], plate)
    viewer_logger.log(sketch_sections(sections), ALIGN_CELL)

    l4 = RowLayout(place=Dir2.CORNER_RT_BT, spacing=2)
    sections = l4.layout_features([[p1, p2]], plate)
    viewer_logger.log(sketch_sections(sections), ALIGN_CELL)


def test_even_col_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(10, 10)
    p2 = Spacer(15, 15)
    p3 = Spacer(20, 20)

    layout = RowLayout(equal_widths=True, spacing=2)
    plate = Rc(60, 30)
    sections = layout.layout_features([[p1, p2, p3]], plate)

    viewer_logger.log(sketch_sections(sections), SINGLE_ROW)


def test_proportional_col_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(10, 10)
    p2 = Spacer(15, 15)
    p3 = Spacer(20, 20)

    layout = RowLayout(spacing=2)
    plate = Rc(60, 30)
    sections = layout.layout_features([[p1, p2, p3]], plate)

    viewer_logger.log(sketch_sections(sections), SINGLE_ROW)


def test_expand_col_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15, more_x=True)

    layout = RowLayout(spacing=2)
    plate = Rc(60, 30)
    sections = layout.layout_features([[p1, p2, p3]], plate)

    viewer_logger.log(sketch_sections(sections), SINGLE_ROW)


def test_expand_two_col_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5, more_x=True)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15, more_x=True)

    layout = RowLayout(spacing=2)
    plate = Rc(60, 30)
    sections = layout.layout_features([[p1, p2, p3]], plate)

    viewer_logger.log(sketch_sections(sections), SINGLE_ROW)


def test_proportional_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(spacing=2)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sections(sections), ROW_LAYOUT)


def test_equal_cols_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(equal_widths=True, spacing=2)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sections(sections), ROW_LAYOUT)


def test_equal_rows_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(equal_heights=True, spacing=2)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sections(sections), ROW_LAYOUT)


def test_equal_rows_cols_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(equal_heights=True, equal_widths=True, spacing=2)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sections(sections), ROW_LAYOUT)


def test_expanding_cols_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    e1 = Spacer(5, 5, more_x=True)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)
    e3 = Spacer(15, 15, more_x=True)

    layout = RowLayout(spacing=2)
    plate = Rc(60, 60)
    sections = layout.layout_features([[e1, p2, p3], [p1, p2, e3]], plate)

    viewer_logger.log(sketch_sections(sections), ROW_LAYOUT)


def test_expanding_row_layout(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    e1 = Spacer(5, 5, more_y=True)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = RowLayout(spacing=2)
    plate = Rc(60, 60)
    sections = layout.layout_features([[e1, p2, p3], [p1, p2, p3]], plate)

    viewer_logger.log(sketch_sections(sections), ROW_LAYOUT)


def test_explict_row_heights(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)
    e3 = Spacer(15, 15, more_x=True)

    layout = RowLayout(row_heights=[14, 44], spacing=(2 / 3))
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3], [p1, p2, e3]], plate)

    viewer_logger.log(sketch_sections(sections), ROW_LAYOUT)


def test_one_row_grid(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3]], plate)
    viewer_logger.log(sketch_sections(sections), GRID_LAYOUT)


def test_one_equal_row_grid(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, equal_widths=True)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3]], plate)
    viewer_logger.log(sketch_sections(sections), GRID_LAYOUT)


def test_one_specified_row_grid(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, col_widths=[5, 20, 15])
    plate = Rc(48, 30)
    sections = layout.layout_features([[p1, p2, p3]], plate)
    viewer_logger.log(sketch_sections(sections), GRID_LAYOUT)


def test_one_expanded_row_grid(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10, more_x=True)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, col_widths=[5, 20, 15])
    plate = Rc(48, 30)
    sections = layout.layout_features([[p1, p2, p3]], plate)
    viewer_logger.log(sketch_sections(sections), GRID_LAYOUT)


def test_sparse_grid(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3], [p1, p2], [p1]], plate)
    viewer_logger.log(sketch_sections(sections), GRID_LAYOUT)


def test_sparse_equal_row_grid(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, equal_heights=True)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3], [p1, p2], [p1]], plate)
    viewer_logger.log(sketch_sections(sections), GRID_LAYOUT)


def test_sparse_equal_grid(viewer_logger: ModelLogger) -> None:
    p1 = Spacer(5, 5)
    p2 = Spacer(10, 10)
    p3 = Spacer(15, 15)

    layout = GridLayout(spacing=2, equal_widths=True, equal_heights=True)
    plate = Rc(60, 60)
    sections = layout.layout_features([[p1, p2, p3], [p1, p2], [p1]], plate)
    viewer_logger.log(sketch_sections(sections), GRID_LAYOUT)
