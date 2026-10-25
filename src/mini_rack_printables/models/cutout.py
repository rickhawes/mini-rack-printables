from typing import override

from ..core.elements_2d import Element2D
from ..core.elements_3d import PrismElement, TubeElement
from ..core.feature import Feature, Rib
from ..core.geometry import Bx, Vec2
from ..core.modeler import Modeler
from ..core.piece import Piece


class Cutout(Feature):
    """
    A cutout of a plate. It can also be outlined with a rib.
    """

    shape: Element2D
    rib: Rib | None

    def __init__(self, shape: Element2D, rib: Rib | None = None) -> None:
        """
        Args:
            shape (Element): The 2D shape to cut out.
            rib (Rib | None): The rib to outline the cutout with.
        """
        self.shape = shape
        self.rib = rib

    @override
    def desired_size(self) -> Feature.DesiredSize:
        rib = 2 * self.rib.width if self.rib is not None else 0
        size = self.shape.size + Vec2(rib, rib)
        return Feature.DesiredSize(size, False)

    @override
    def render(self, plate: Bx) -> list[Piece]:
        """Returns a list of PartOutput structures representing the cutout"""
        # the same rendering formula is used for all types of cutouts
        md = Modeler.make_on_bx(plate)
        md.add_element(PrismElement(self.shape, plate.size.z), cut=True)

        if self.rib is not None:
            rib = TubeElement(self.shape, self.rib.width, self.rib.depth)
            md.add_element(rib)

        return md.all_pieces()
