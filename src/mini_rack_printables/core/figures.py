"""
2d figures for models. Figures are the primitives that make up models and parts.
They are built to be easily combined and rendered.
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence, override

import build123d as bd

from .corners import Corners, RoundedCorners, SquareCorners
from .geometry import Ax2, AxDir, Degree, Mm, Rc, Vec2
from .hole_patterns import HolePattern, fill_holes
from .print_dims import E

#
# region Base classes
#


@dataclass(frozen=True)
class Op2:
    """Wrap the figure in this class to specify how to combine figures."""

    figure: Figure
    """Figure to combine"""
    pos: Vec2 = Vec2(0, 0)
    """offset the figure"""
    angle: Degree = 0
    """rotate the figure"""
    cut: bool = False
    """cut (i.e. subtract) the figure"""

    def to_location(self) -> bd.Location:
        """Covert `pos` to `Location`."""
        return bd.Location((self.pos.y, self.pos.y), angle=self.angle)

    def to_mode(self) -> bd.Mode:
        """Convert `cut` to the `Mode`."""
        return bd.Mode.SUBTRACT if self.cut else bd.Mode.ADD

    def to_bounds(self) -> Rc:
        """Return the bounding rectangle of the shape with the given `op`"""
        sin = math.sin(math.radians(self.angle))
        cos = math.cos(math.radians(self.angle))
        size = self.figure.size
        dx = abs(size.y * sin + size.x * cos)
        dy = abs(size.y * cos + size.x * sin)
        return Rc(Vec2(dx, dy), self.pos)


class Figure(ABC):
    """ABC for the 2d shapes that are used to form 3d shapes."""

    @property
    @abstractmethod
    def size(self) -> Vec2:
        """Returns the size of the shape in 2d without any rotation"""

    @abstractmethod
    def sketch(self) -> bd.Sketch:
        """Draw the outline of the shape according to the `op` ignoring
        the `op.block` field."""

    def calc_interior(self, inset: Vec2) -> Rc:
        """Calculate an area that is in the interior of this figure
        with the specified inset.

        Used to optimize hole fills. Return an empty rect if not easily
        calculated.
        """
        _ = inset
        return Rc(0, 0)


# endregion

#
# region Specific figures
#


class CircleFigure(Figure):
    """A circle figure with a `radius`."""

    radius: Mm

    def __init__(self, radius: Mm, holes: HolePattern | None = None) -> None:
        """
        Args:
            radius (Mm): The radius of the circle.
        """
        self.radius = radius
        self.holes = holes

    @property
    @override
    def size(self) -> Vec2:
        return Vec2(2 * self.radius, 2 * self.radius)

    @override
    def sketch(self) -> bd.Sketch:
        sk = bd.Circle(self.radius)
        if self.holes is not None:
            sk = fill_holes(sk, self.size, self.holes)
        return sk


class RectangleFigure(Figure):
    """A rectangle shape or rounded rectangle shape."""

    width: Mm
    height: Mm
    corners: Corners
    holes: HolePattern | None

    def __init__(
        self,
        width: Mm,
        height: Mm,
        corners: Mm | Corners | None = None,
        holes: HolePattern | None = None,
    ) -> None:
        """
        Args:
            width (Mm): The width of the rectangle.
            height (Mm): The height of the rectangle.
            corners (Corners): The corner shape of the rectangle.
                If a `Mm` > 0, then a Rounded Corner is used.
        """
        self.width = width
        self.height = height
        if isinstance(corners, (int, float)):
            self.corners = RoundedCorners(corners)
        elif corners is None:
            self.corners = SquareCorners(0)
        else:
            self.corners = corners
        self.holes = holes

    @property
    @override
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    @override
    def sketch(self) -> bd.Sketch:
        def complex_corners() -> bd.Sketch:
            cs = self.corners.size
            cw, ch = cs.x, cs.y
            dx, dy = (self.width / 2) - cw, (self.height / 2) - ch
            with bd.BuildSketch() as sk:
                with bd.BuildLine():
                    # side lines
                    l_top = bd.Line((-dx, dy + ch), (dx, dy + ch))
                    l_right = bd.Line((dx + cw, dy), (dx + cw, -dy))
                    l_bottom = bd.Line((dx, -dy - ch), (-dx, -dy - ch))
                    l_left = bd.Line((-dx - cw, -dy), (-dx - cw, dy))
                    # corners
                    self.corners.draw(l_top @ 1, l_right @ 0, Corners.TOP_RIGHT)
                    self.corners.draw(l_right @ 1, l_bottom @ 0, Corners.BOTTOM_RIGHT)
                    self.corners.draw(l_bottom @ 1, l_left @ 0, Corners.BOTTOM_LEFT)
                    self.corners.draw(l_left @ 1, l_top @ 0, Corners.TOP_LEFT)
                _ = bd.make_face()
            return bd.Sketch(sk.sketch)

        # Optimize the square and rounded corners cases
        def solid_fill() -> bd.Sketch:
            match self.corners:
                case SquareCorners():
                    return bd.Rectangle(self.width, self.height)
                case RoundedCorners() if self.corners.radius == 0:
                    return bd.Rectangle(self.width, self.height)
                case RoundedCorners():
                    return bd.RectangleRounded(
                        self.width, self.height, self.corners.radius
                    )
                case _:
                    return complex_corners()

        sk = solid_fill()
        if self.holes is not None:
            interior_size = self.size - (
                self.corners.size if self.corners is not None else Vec2(0, 0)
            )
            sk = fill_holes(sk, self.size, self.holes, Rc(interior_size))
        return sk


class SlotFigure(Figure):
    """A slot shape."""

    width: Mm
    height: Mm
    holes: HolePattern | None

    def __init__(self, width: Mm, height: Mm, holes: HolePattern | None = None) -> None:
        """
        Args:
            width (Mm): The width of the slot.
            height (Mm): The height of the slot.
        """
        self.width = width
        self.height = height
        self.holes = holes

    @property
    @override
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    @override
    def sketch(self) -> bd.Sketch:
        sk = bd.SlotOverall(self.width, self.height)
        if self.holes is not None:
            sk = fill_holes(sk, self.size, self.holes)
        return sk


class TrapezoidFigure(Figure):
    """A trapezoid shape with the major width on the bottom and minor on the top."""

    width: Mm
    height: Mm
    angle1: float
    angle2: float | None = None
    minor_width: Mm | None = None
    holes: HolePattern | None

    def __init__(
        self,
        width: Mm,
        height: Mm,
        angle1: float | None = 90,
        angle2: float | None = None,
        holes: HolePattern | None = None,
    ) -> None:
        """
        A trapezoid shape with the major width on the bottom and minor on the top.

        Args:
            width (Mm): The major width of the trapezoid.
            height (Mm): The height of the trapezoid.
            angle1 (Mm): The interior angle of the first side. Defaults to 90.
            angle2 (Mm): The interior angle of the second side. Defaults to angle1.
        """
        if angle1 is None and angle2 is None:
            raise ValueError("either angle1 or angle2 must be specified.")
        if angle1 is None and angle2 is not None:
            angle1 = angle2
        elif angle2 is None and angle1 is not None:
            angle2 = angle1
        assert angle1 is not None and angle2 is not None

        self.width = width
        self.height = height
        self.angle1 = angle1
        self.angle2 = angle2
        self.holes = holes

    @property
    @override
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    @override
    def sketch(self) -> bd.Sketch:
        sk = bd.Trapezoid(
            self.width,
            self.height,
            left_side_angle=self.angle1,
            right_side_angle=self.angle2,
        )
        if self.holes is not None:
            sk = fill_holes(sk, self.size, self.holes)
        return sk

    @staticmethod
    def angle_from_widths(
        major_width: Mm,
        minor_width: Mm,
        height: Mm,
        angle1: Degree | None = None,
        angle2: Degree | None = None,
    ) -> Degree:
        """Calculate angle given widths and height and the other angle"""

        # Calculate angle1 or angle2 based on minor_width
        if angle1 is not None and angle2 is None:
            reduction_left = (
                0 if angle1 == 90 else height / math.tan(math.radians(angle1))
            )
            return math.degrees(
                math.atan(height / (major_width - minor_width - reduction_left))
            )
        if angle1 is None and angle2 is not None:
            reduction_right = (
                0 if angle2 == 90 else height / math.tan(math.radians(angle2))
            )
            return math.degrees(
                math.atan(height / (major_width - minor_width - reduction_right))
            )
        return math.degrees(math.atan(2 * height / (major_width - minor_width)))


class TriangleFigure(Figure):
    """A triangle shape, by default it is an iso-triangle"""

    width: Mm
    height: Mm
    tip_ratio: float
    holes: HolePattern | None

    def __init__(
        self,
        width: Mm,
        height: Mm,
        tip_ratio: float = 0.0,
        holes: HolePattern | None = None,
    ) -> None:
        """
        Args:
            width (Mm): The width of the triangle.
            height (Mm): The height of the triangle.
        """
        self.width = width
        self.height = height
        self.tip_ratio = tip_ratio
        self.holes = holes

    @property
    @override
    def size(self) -> Vec2:
        return Vec2(max(self.width, abs(self.tip_ratio * self.width / 2)), self.height)

    @override
    def sketch(self) -> bd.Sketch:
        dx, dy = self.width / 2, self.height / 2
        tip_x = self.tip_ratio * dx
        pts = [(-dx, -dy), (tip_x, dy), (dx, -dy)]
        sk = bd.make_face(bd.Polyline(pts, close=True))
        if self.holes is not None:
            sk = fill_holes(sk, self.size, self.holes)
        return sk


# endregion

#
# region Figures that combine other figures together
#


class CombinedFigure(Figure):
    """Combine a set of figures into another figure."""

    ops: Sequence[Op2]

    def __init__(self, ops: Sequence[Op2]) -> None:
        self.ops = ops

    @override
    @property
    def size(self) -> Vec2:
        return Rc.union(*(op.to_bounds() for op in self.ops)).size

    @override
    def sketch(self) -> bd.Sketch:
        sk = bd.Sketch()
        for op in self.ops:
            if op.cut:
                sk = bd.Sketch(
                    sk
                    - (
                        bd.Location(op.pos.to_vector(), angle=op.angle)
                        * op.figure.sketch()
                    )
                )
            else:
                sk = bd.Sketch(
                    sk
                    + bd.Location(op.pos.to_vector(), angle=op.angle)
                    * op.figure.sketch()
                )
        return bd.Sketch(sk)


class AlignedFigure(CombinedFigure):
    """A combined figure with all the figures aligned along an axis."""

    axis: Ax2
    align: AxDir

    def __init__(
        self, figures: Sequence[Figure], axis: Ax2 = Ax2.X, align: AxDir = AxDir.CENTER
    ) -> None:
        self.axis = axis
        self.align = align

        fig_rcs = [Rc(fig.size) for fig in figures]
        arranged_rcs = Rc.arrange(axis, align, *fig_rcs)
        fig_ops = [Op2(fig, rc.center) for rc, fig in zip(arranged_rcs, figures)]
        super().__init__(fig_ops)


class CutoutFigure(CombinedFigure):
    """Create an figure that has a `base` with a `cutout` figures"""

    base: Figure
    cutout: Figure

    def __init__(self, base: Figure, cutout: Figure) -> None:
        fig_ops = [Op2(base), Op2(cutout, cut=True)]
        super().__init__(fig_ops)
        self.base = base
        self.cutout = cutout


class OutsetFigure(Figure):
    """Create an figure that is a `base` figure that is outset by `amount`"""

    base: Figure
    """The base shape"""
    outset: Mm
    """The outset amount (may be negative for an inset)"""

    def __init__(self, base: Figure, outset: Mm) -> None:
        if abs(outset) < E:
            raise ValueError("outset must not be 0")
        self.base = base
        self.outset = outset

    @override
    @property
    def size(self) -> Vec2:
        return (
            self.base.size
            if self.outset < 0
            else self.base.size + Vec2(2 * self.outset, 2 * self.outset)
        )

    @override
    def sketch(self) -> bd.Sketch:
        base = self.base.sketch()
        return bd.Sketch(bd.offset(base, self.outset))


class RotatedFigure(Figure):
    """Create an figure that is a `base` rotated by `angle`"""

    base: Figure
    """The base shape"""
    angle: Degree
    """The outset amount (may be negative for an inset)"""
    _op2: Op2

    def __init__(self, base: Figure, angle: Degree) -> None:
        self.base = base
        self.angle = angle
        self._op2 = Op2(base, angle=angle)

    @override
    @property
    def size(self) -> Vec2:
        return self._op2.to_bounds().size

    @override
    def sketch(self) -> bd.Sketch:
        return self._op2.to_location() * self.base.sketch()


class RingFigure(CombinedFigure):
    """Create a figure that is a ring of a `base` figure."""

    base: Figure
    outset: Mm

    def __init__(self, base: Figure, outset: Mm) -> None:
        outset_fig = OutsetFigure(base, outset)
        outer, inner = (outset_fig, base) if outset > 0 else (base, outset_fig)
        fig_ops = [Op2(outer), Op2(inner, cut=True)]
        super().__init__(fig_ops)
        self.base = base
        self.outset = outset


# endregion
