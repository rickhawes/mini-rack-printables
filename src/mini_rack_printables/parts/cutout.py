from typing import override

from ..geometry import Rib, Vec2
from .model_feature import ModelFeature, FeaturePiece, PlatePlanes
from ..elements_2d import Element2D
from ..elements_3d import extrude_element, extrude_tube
from build123d import Mode


class Cutout(ModelFeature):
    """
    A cutout of a plate. It can also be outlined with a rib.
    """

    shape: Element2D
    rib: Rib | None

    def __init__(self, shape: Element2D, rib: Rib | None = None):
        """
        Args:
            shape (Element): The 2D shape to cut out.
            rib (Rib | None): The rib to outline the cutout with.
        """
        self.shape = shape
        self.rib = rib

    @override
    def desired_size(self) -> ModelFeature.DesiredSize:
        rib = 2 * self.rib.width if self.rib else 0
        size = self.shape.size() + Vec2(rib, rib)
        return ModelFeature.DesiredSize(size, False)

    @override
    def render(self, plate_planes: PlatePlanes) -> list[FeaturePiece]:
        """Returns a list of PartOutput structures representing the cutout"""
        # the same rendering formula is used for all types of cutouts
        hole = plate_planes.bottom_plane * extrude_element(self.shape, plate_planes.depth)
        result = [FeaturePiece(hole, Mode.SUBTRACT)]

        if self.rib:
            rib = plate_planes.top_plane * extrude_tube(
                self.shape, self.rib.width, self.rib.depth
            )
            result += [FeaturePiece(rib)]

        return result
