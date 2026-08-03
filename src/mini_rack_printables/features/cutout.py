from .model_feature import ModelFeature, FeatureParts
from build123d import Vector, extrude, offset, Circle, BuildSketch, Mode, add


class Cutout(ModelFeature):
    radius: float
    rib_size: Vector

    def __init__(self, radius: float, rib_size: Vector):
        self.radius = radius
        self.rib_size = rib_size

    def render(self, plate_size: Vector) -> FeatureParts:
        cir = Circle(self.radius)
        with BuildSketch() as sk:
            add(offset(cir, amount=self.rib_size.X), mode=Mode.ADD)
            add(cir, mode=Mode.SUBTRACT)
        extruded_rib = extrude(sk.sketch, amount=self.rib_size.Y) if self.rib_size.X > 0 else None
        return FeatureParts(
            addition=extruded_rib,
            subtraction=extrude(cir, amount=plate_size.Z),
        )
