from mini_rack_printables import (
    AlignedFigure,
    Ax2,
    AxDir,
    BeveledCorners,
    CircleFigure,
    CircleFill,
    HexFill,
    InsetCorners,
    Op2,
    RectangleFigure,
    RotatedFigure,
    RoundedCorners,
    SelectedCorners,
    SlotFigure,
    SquareFill,
    TestLogger,
    TrapezoidFigure,
    TriangleFigure,
)
from mini_rack_printables.core.figures import CombinedFigure, CutoutFigure, RingFigure

# test by rendering a bunch of figures

RECT = "Rectangle tests"
FILL = "Fill tests"
SHAPE = "Shape tests"
COMBINED = "Combined tests"


def test_rectangle_figure(viewer_logger: TestLogger) -> None:
    fig = RectangleFigure(width=40, height=20)
    viewer_logger.log(fig.sketch(), RECT)


def test_rounded_corners(viewer_logger: TestLogger) -> None:
    fig = RectangleFigure(width=40, height=20, corners=4)
    viewer_logger.log(fig.sketch(), RECT)


def test_inset_corners(viewer_logger: TestLogger) -> None:
    fig = RectangleFigure(40, 20, InsetCorners(5))
    viewer_logger.log(fig.sketch(), RECT)


def test_beveled_corners(viewer_logger: TestLogger) -> None:
    fig = RectangleFigure(40, 20, BeveledCorners(4, 6))
    viewer_logger.log(fig.sketch(), RECT)


def test_selected_corners(viewer_logger: TestLogger) -> None:
    fig = RectangleFigure(
        40, 20, SelectedCorners(RoundedCorners(6), top_left=True, bottom_right=True)
    )
    viewer_logger.log(fig.sketch(), RECT)


def test_hex_fill(viewer_logger: TestLogger) -> None:
    fig1 = RectangleFigure(width=40, height=20, holes=HexFill())
    viewer_logger.log(fig1.sketch(), FILL)
    fig2 = CircleFigure(15, holes=HexFill())
    viewer_logger.log(fig2.sketch(), FILL)
    fig3 = TrapezoidFigure(width=40, height=20, angle1=80, holes=HexFill())
    viewer_logger.log(fig3.sketch(), FILL)


def test_empty_fill(viewer_logger: TestLogger) -> None:
    fig = RectangleFigure(width=40, height=10, corners=4)
    viewer_logger.log(fig.sketch(), FILL)


def test_circular_fill(viewer_logger: TestLogger) -> None:
    fig = RectangleFigure(width=40, height=30, corners=4, holes=CircleFill())
    viewer_logger.log(fig.sketch(), FILL)


def test_square_fill(viewer_logger: TestLogger) -> None:
    fig = RectangleFigure(width=40, height=20, corners=4, holes=SquareFill())
    viewer_logger.log(fig.sketch(), FILL)


def test_partial_fill(viewer_logger: TestLogger) -> None:
    fig1 = TriangleFigure(width=40, height=20, holes=SquareFill())
    viewer_logger.log(fig1.sketch(), FILL)


def test_circle_figure(viewer_logger: TestLogger) -> None:
    fig = CircleFigure(radius=10)
    viewer_logger.log(fig.sketch(), SHAPE)


def test_slot_figure(viewer_logger: TestLogger) -> None:
    fig = SlotFigure(40, 20)
    viewer_logger.log(fig.sketch(), SHAPE)


def test_trapezoid_figure(viewer_logger: TestLogger) -> None:
    fig1 = TrapezoidFigure(40, 20, angle1=80)
    viewer_logger.log(fig1.sketch(), SHAPE)
    angle2 = TrapezoidFigure.angle_from_widths(
        major_width=40, minor_width=10, height=20, angle1=90
    )
    fig2 = TrapezoidFigure(40, 20, angle1=90, angle2=angle2)
    viewer_logger.log(fig2.sketch(), SHAPE)


def test_triangle_figure(viewer_logger: TestLogger) -> None:
    fig = TriangleFigure(width=40, height=20)
    viewer_logger.log(fig.sketch(), SHAPE)
    fig2 = TriangleFigure(width=40, height=20, tip_ratio=1.0)
    viewer_logger.log(fig2.sketch(), SHAPE)


def test_modes(viewer_logger: TestLogger) -> None:
    fig1 = RectangleFigure(40, 40)
    fig2 = CircleFigure(15)
    fig3 = TriangleFigure(35, 35)
    c1 = CombinedFigure([Op2(fig1)])
    viewer_logger.log(c1.sketch(), COMBINED)
    c2 = CombinedFigure([Op2(fig1), Op2(fig2, cut=True)])
    viewer_logger.log(c2.sketch(), COMBINED)
    c3 = CombinedFigure([Op2(fig1), Op2(fig2, cut=True), Op2(fig3, angle=90)])
    viewer_logger.log(c3.sketch(), COMBINED)


def test_ring_figure(viewer_logger: TestLogger) -> None:
    fig1 = TriangleFigure(35, 35)
    fig2 = RingFigure(fig1, 2)
    viewer_logger.log(fig2.sketch(), COMBINED)
    fig3 = RingFigure(fig1, -2)


def test_cutout_figure(viewer_logger: TestLogger) -> None:
    fig1 = RectangleFigure(40, 40)
    fig2 = CircleFigure(15)
    fig3 = CutoutFigure(fig1, fig2)
    viewer_logger.log(fig3.sketch(), COMBINED)


def test_aligned_figures(viewer_logger: TestLogger) -> None:
    fig1 = RectangleFigure(5, 2)
    angle2 = TrapezoidFigure.angle_from_widths(
        major_width=10, minor_width=2, height=15, angle1=90
    )
    fig2 = RotatedFigure(TrapezoidFigure(10, 15, angle1=90, angle2=angle2), 90)
    fig3 = RectangleFigure(20, 10)
    fig4 = AlignedFigure([fig1, fig2, fig3], axis=Ax2.X, align=AxDir.MINUS)
    viewer_logger.log(fig4.sketch(), COMBINED)
