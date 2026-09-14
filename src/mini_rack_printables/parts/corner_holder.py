from build123d import Sketch, Vector, extrude

from ..elements import (
    InsetCorners,
    RectangleElement,
    Element2D,
    sketch_ring,
)
from ..selectors import Place
from .model_part import ModelPart, PartPiece, Plate


class CornerHolder(ModelPart):
    """
    A device holder for a single device on a shelf. Devices are held by friction from the corners. The corners
    are cut out of holder's shape.
    """

    def __init__(
        self,
        element: Element2D,
        corner_width: float = 10.0,
        corner_height: float = 10.0,
        wall_depth: float = 5.0,
        wall_thickness: float = 3.0,
        align: Place = Place.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0.0,
    ):
        """
        Initialize a holder with the given style, device size, and optional label, align, shift, and padding.

        Args:
            shape (PrimativeShape): The shape of the device to hold.
            corner_width (float): The width of the corner cutout. Defaults to 5.0.
            corner_height (float): The height of the corner cutout. Defaults to 5.0.
            wall_depth (float): The depth of the holder's corner. Defaults to 5.0.
            wall_thickness (float): The thickness of the holder's wall. Defaults to 3.0.
            align (Selector): The alignment of the holder on the plate. Defaults to Selector.CENTER.
            shift (Vector): The shift of the holder on the plate. Defaults to Vector(0, 0).
            padding (float): The padding around the holder. Defaults to 0.0.
        """
        assert corner_height >= 0 and corner_width >= 0, (
            "corner_height and corner_width must be non-negative"
        )
        assert wall_thickness > 0.5, "wall_thickness must be positive"
        super().__init__(align, shift, padding)
        self.element = element
        self.wall_thickness = wall_thickness
        self.wall_depth = wall_depth
        self.corner_width = corner_width
        self.corner_height = corner_height
        assert self.element.size().X > 2 * corner_width, (
            "shape width must be greater than 2 * corner_width"
        )
        assert self.element.size().Y > 2 * corner_height, (
            "shape height must be greater than 2 * corner_height"
        )

    def layout_size(self, plate_size: Vector) -> Vector:
        return self.element.size() + 2 * Vector(self.wall_thickness, self.wall_thickness)

    def render(self, plate: Plate) -> list[PartPiece]:
        # dimensions
        w, d = self.wall_thickness, self.wall_depth
        cw = self.corner_width
        size = self.element.size()

        # sketch the holder shape
        cross = RectangleElement(size.X + 2 * w, size.Y + 2 * w, InsetCorners(cw + 2 * w))
        sk = Sketch(sketch_ring(self.element, w) - cross.sketch())
        return [PartPiece(plate.top_plane * extrude(sk, d))]
