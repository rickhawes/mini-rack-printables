from ..selector import Selector
from ..geometry import Rib
from .model_part import ModelPart, PartPiece, Plate
from ..elements import Element, extrude_element, extrude_tube
from build123d import Vector, Mode


class Cutout(ModelPart):
    """
    A cutout of a plate can be a circle, a rectangle, or a slot in shape. It can also be outlined with a rib.
    """

    element: Element
    size: Vector
    radius: float
    rib: Rib | None

    def __init__(
        self,
        element: Element,
        rib: Rib | None = None,
        align: Selector = Selector.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0,
    ):
        """
        Args:
            element (Element): The element shape to cut out.
            rib (Rib | None): The rib to outline the cutout with.
            align (Selector): The alignment of the cutout on the plate.
            shift (Vector): The shift of the cutout on the plate.
            padding (float): The padding around the cutout.
        """
        super().__init__(align, shift, padding)
        self.element = element
        self.rib = rib

    def layout_size(self, plate_size: Vector) -> Vector:
        shape_size = self.element.size()
        rib_width = self.rib.width if self.rib else 0
        return Vector(
            shape_size.X + rib_width * 2,
            shape_size.Y + rib_width * 2,
        )

    def render(self, plate: Plate) -> list[PartPiece]:
        """Returns a list of PartOutput structures representing the cutout"""
        # the same rendering formula is used for all types of cutouts
        hole = plate.bottom_plane * extrude_element(self.element, plate.size.Z)
        result = [PartPiece(hole, Mode.SUBTRACT)]

        if self.rib:
            rib = plate.top_plane * extrude_tube(self.element, self.rib.width, self.rib.depth)
            result += [PartPiece(rib)]

        return result
