from ..geometry import RcAlignment, AlignmentVector
from .model_part import ModelPart, PartPiece, Plate
from build123d import (
    Vector,
    extrude,
    offset,
    Circle,
    BuildSketch,
    Mode,
    add,
    Sketch,
    Rectangle,
    RectangleRounded,
    SlotOverall,
)
from enum import Enum, auto


class CutoutType(Enum):
    """
    The shape of hole for a Cutout.
    """

    CIRCLE = auto()
    RECTANGLE = auto()
    SLOT = auto()


class Cutout(ModelPart):
    """
    A cutout of a plate can be a circle, a rectangle, or a slot in shape. It can also be outlined with a rib.
    """

    type: CutoutType
    size: Vector
    radius: float
    rib_size: Vector

    def __init__(
        self,
        type: CutoutType,
        size: Vector = Vector(0, 0),
        radius: float = 0,
        rib_size: Vector = Vector(0, 0),
        label: str = "Cutout",
        align: AlignmentVector = RcAlignment.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0,
    ):
        assert type != CutoutType.CIRCLE or radius > 0, (
            f"Circle cutout requires a postive radius: {radius}"
        )
        assert type != CutoutType.RECTANGLE or (size.X > 0 and size.Y > 0), (
            f"Rectangle cutout requires a size: {size}"
        )
        assert type != CutoutType.SLOT or radius == 0, (
            f"Slot cutout should not have a radius: {radius}"
        )

        super().__init__(label, align, shift, padding)
        self.type = type
        self.size = size
        self.radius = radius
        self.rib_size = rib_size

    def layout_size(self, plate_size: Vector) -> Vector:
        match self.type:
            case CutoutType.CIRCLE:
                return Vector(
                    (self.radius + self.rib_size.X) * 2, (self.radius + self.rib_size.X) * 2
                )
            case CutoutType.RECTANGLE:
                return Vector(
                    self.size.X + self.rib_size.X * 2, self.size.Y + self.rib_size.Y * 2
                )
            case CutoutType.SLOT:
                return Vector(
                    self.size.X + self.rib_size.X * 2, self.size.Y + self.rib_size.Y * 2
                )

    def sketch_outline(self) -> Sketch:
        """Returns the outline of the cutout as a Sketch"""
        with BuildSketch() as sk:
            match self.type:
                case CutoutType.CIRCLE:
                    Circle(self.radius)
                case CutoutType.RECTANGLE:
                    if self.radius > 0:
                        RectangleRounded(
                            width=self.size.X, height=self.size.Y, radius=self.radius
                        )
                    else:
                        Rectangle(width=self.size.X, height=self.size.Y)
                case CutoutType.SLOT:
                    SlotOverall(width=self.size.X, height=self.size.Y)
        return sk.sketch

    def render(self, plate: Plate) -> list[PartPiece]:
        """Returns a list of PartOutput structures representing the cutout"""
        # the same rendering formula is used for all types of cutouts
        outline = self.sketch_outline()
        hole = extrude(plate.bottom_plane * outline, amount=plate.size.Z)
        hole.label = self.label
        result = [PartPiece(self.label, hole.solid(), mode=Mode.SUBTRACT)]

        if self.rib_size.X > 0:
            with BuildSketch() as sk:
                add(offset(outline, amount=self.rib_size.X), mode=Mode.ADD)
                add(outline, mode=Mode.SUBTRACT)
            rib = extrude(plate.top_plane * sk.sketch, amount=self.rib_size.Y)
            rib.label = self.label
            result += [PartPiece(self.label, rib.solid())]

        return result
