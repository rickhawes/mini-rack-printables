from dataclasses import dataclass
from typing import final, override

from ..core.elements_2d import RectangleElement, TrapezoidElement
from ..core.elements_3d import PrismElement
from ..core.feature import FeatureList, Rib
from ..core.geometry import AxDir3, Dir2, Mm, Rc, Vec2, Vec3
from ..core.layouts import Layout, RowLayout
from ..core.model import Model
from ..core.modeler import Modeler
from .rack_dims import RackDims, ShelfTabDims
from .rack_holes import RackHolePattern


@final
class Faceplate(Model):
    """
    A mini-rack faceplate model. The model can be customized by
    rack-unit sizes and features.
    """

    @dataclass(frozen=True)
    class Style:
        """Style parameters for the faceplate"""

        thickness: Mm = 3.0
        """Thickness of the plate"""
        rounding: Mm = 3.0
        """Rounding applied to corners of a face_plate"""
        middle_holes: bool = True
        """Draw middle screw holes"""
        half_height_bottom: bool = False
        """Start the bottom with a half unit"""
        rib: Rib = Rib(2.0, 1.0)
        """Rib size for the plate"""

    STD_RIB = Rib(2.0, 1.0)
    """Standard rib size"""

    NO_RIB = Rib(0, 0)
    """No rib size"""

    STD_WITH_RIB = Style(rib=Rib(2.0, 1.0))
    """Standard style with rib"""

    PLAIN = Style(rib=Rib(0, 0))
    """Standard style without rib"""

    rack_units: float
    """Rack units of the plate"""
    style: Style
    features: FeatureList | None = None
    layout: Layout = RowLayout()

    def __init__(
        self,
        rack_units: float,
        style: Style | None = None,
        features: FeatureList | None = None,
        layout: Layout | None = None,
    ) -> None:
        """
        Create a faceplate model

        Args:
            rack_units: Number of rack units of the plate with half units being acceptable
            style: Style options for the plate
            features: The feature to use for the plate. Defaults to None.
            layout: The layout options for the plate. Defaults to None for a RowLayout
        """
        self.rack_units = rack_units
        self.style = style if style is not None else Faceplate.Style()
        self.features = features
        self.layout = layout if layout is not None else RowLayout()

    @override
    def render(self) -> Model.Rendering:
        """
        Render the faceplate

        Returns:
            A compound shape of the faceplate.
        """
        plate_size = Vec2(RackDims.WIDTH_10INCH, self.rack_units * RackDims.HEIGHT_1U)
        feature_area = Rc(ShelfTabDims.MAX_DX_TABS, plate_size.y - 2 * self.style.rib.width)

        # form a round-rect base with cutout for the holes of the rack screws
        base_2d = RectangleElement(
            plate_size.x,
            plate_size.y,
            corners=self.style.rounding,
            holes=RackHolePattern(
                self.rack_units, self.style.middle_holes, self.style.half_height_bottom
            ),
        )
        base = PrismElement(base_2d, self.style.thickness)

        # create a modeler to place the other elements
        md = Modeler.make_with_element(base)

        # ribs
        if self.style.rib.depth > 0:

            def add_rib(dir2: Dir2) -> None:
                rib_size = Vec3(feature_area.size.x, self.style.rib.width, self.style.rib.depth)
                rib_bx = md.place_bx(rib_size, dir2)
                # place the sub assembly on the side
                rib_md = md.add_modeler_on_bx(rib_bx, AxDir3.Y_MINUS, AxDir3.Y_PLUS)
                rib_elem = PrismElement(TrapezoidElement(rib_size.x, rib_size.z, 30), rib_size.y)
                rib_md.add_element(rib_elem)

            add_rib(Dir2.Y_PLUS)
            add_rib(Dir2.Y_MINUS)

        # features
        if self.features is not None:
            md.add_features(self.features, feature_area, self.layout)

        return md.render()
