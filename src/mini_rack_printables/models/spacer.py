from typing import override

from ..core.feature import Feature, FeaturePiece
from ..core.geometry import Mm, Vec2


class Spacer(Feature):
    """A spacer that does nothing fill space to help with the layout of a plate."""

    width: Mm
    height: Mm
    more_x: bool
    more_y: bool

    def __init__(self, width: Mm, height: Mm, more_x: bool = False, more_y: bool = False):
        self.width = width
        self.height = height
        self.more_x = more_x
        self.more_y = more_y

    @override
    def desired_size(self) -> Feature.DesiredSize:
        return Feature.DesiredSize(Vec2(self.width, self.height), self.more_x, self.more_y)

    @override
    def render(self, plate_planes: PlatePlanes) -> list[FeaturePiece]:
        return []
