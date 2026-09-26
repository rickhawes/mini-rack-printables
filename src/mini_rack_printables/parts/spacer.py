from .model_part import ModelPart, PlatePlanes, PartPiece


class Spacer(ModelPart):
    """A spacer that does nothing fill space to help with the layout of a plate."""

    def __init__(self, width: float, height: float, more_x: bool = False, more_y: bool = False):
        self.width = width
        self.height = height
        self.more_x = more_x
        self.more_y = more_y

    def desired_size(self) -> ModelPart.DesiredSize:
        return ModelPart.DesiredSize((self.width, self.height), self.more_x, self.more_y)

    def render(self, plate_planes: PlatePlanes) -> list[PartPiece]:
        return []
