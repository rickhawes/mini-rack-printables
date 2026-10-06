from .model_part import ModelPart, PlatePlanes, PartPiece
from ..geometry import Vec2, Mm
from typing import override


class Spacer(ModelPart):
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
    def desired_size(self) -> ModelPart.DesiredSize:
        return ModelPart.DesiredSize(Vec2(self.width, self.height), self.more_x, self.more_y)

    @override
    def render(self, plate_planes: PlatePlanes) -> list[PartPiece]:
        return []
