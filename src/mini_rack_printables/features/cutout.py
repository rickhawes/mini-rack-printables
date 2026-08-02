from .model_feature import ModelFeature, FeatureParts
from build123d import Vector, extrude, offset, Circle


class Cutout(ModelFeature):
    radius: float
    rib_size: Vector

    def __init__(self, radius: float, rib_size: Vector):
        self.radius = radius
        self.rib_size = rib_size

    def render(self, plate_size: Vector) -> FeatureParts:
        cir = Circle(self.radius)
        return FeatureParts(
            addition=extrude(
                (offset(cir, amount=self.rib_size.X) - cir), amount=self.rib_size.Y
            )
            if self.rib_size.X > 0
            else None,
            subtraction=extrude(cir, amount=plate_size.Z),
        )
