from ..core.model_feature import ModelFeature, PlatePlanes, FeaturePiece
from ..core.geometry import Vec2, Mm
from typing import override


class Spacer(ModelFeature):
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
    def desired_size(self) -> ModelFeature.DesiredSize:
        return ModelFeature.DesiredSize(Vec2(self.width, self.height), self.more_x, self.more_y)

    @override
    def render(self, plate_planes: PlatePlanes) -> list[FeaturePiece]:
        return []
