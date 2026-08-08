from ..geometry import RcAlignment, AlignmentVector
from .model_part import ModelPart, PartPiece, Plate
from ..primative_shapes import PrimativeShape, make_primative_prism, make_primative_tube
from build123d import Vector, Mode, VectorLike


class Cutout(ModelPart):
    """
    A cutout of a plate can be a circle, a rectangle, or a slot in shape. It can also be outlined with a rib.
    """

    shape: PrimativeShape
    size: Vector
    radius: float
    rib_size: Vector

    def __init__(
        self,
        shape: PrimativeShape,
        rib_size: VectorLike = (0, 0),
        label: str = "Cutout",
        align: AlignmentVector = RcAlignment.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0,
    ):
        super().__init__(label, align, shift, padding)
        self.shape = shape
        self.rib_size = Vector(rib_size)

    def layout_size(self, plate_size: Vector) -> Vector:
        shape_size = self.shape.size()
        return Vector(
            shape_size.X + self.rib_size.X * 2,
            shape_size.Y + self.rib_size.Y * 2,
        )

    def render(self, plate: Plate) -> list[PartPiece]:
        """Returns a list of PartOutput structures representing the cutout"""
        # the same rendering formula is used for all types of cutouts
        hole = plate.bottom_plane * make_primative_prism(self.shape, plate.size.Z)
        result = [PartPiece(self.label, hole.solid(), mode=Mode.SUBTRACT)]

        if self.rib_size.X > 0:
            rib = plate.top_plane * make_primative_tube(self.shape, self.rib_size.X, self.rib_size.Y)
            result += [PartPiece(self.label, rib.solid())]

        return result
