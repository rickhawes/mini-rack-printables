"""
3D Elements for models and parts. Elements are the primitives that are to form a model.

See Also:
    Elements2d - for the two equivalent
"""

from abc import ABC, abstractmethod
from typing import override, Sequence
from functools import cached_property
from importlib.resources import as_file, files
from pathlib import Path

from build123d import Cone, Cylinder, Location, Part, Sketch, extrude, offset, Mesher, TopoDS_Solid, Unit, Vector, import_brep, Shape, CenterOf

from .corners import Corners
from .elements_2d import Element2D, RectangleElement, RingElement
from .geometry import Degree, Mm, Vec3
from .hole_patterns import HolePattern
from .piece import Piece


class Element3D(ABC):
    """3d shapes that are composable by an `Assembler`"""

    @property
    @abstractmethod
    def size(self) -> Vec3:
        """Returns the size of the shape in 3d."""

    @abstractmethod
    def render(self, cut: bool = False) -> Piece:
        """Extrudes the shape centered on the plane and the z-axis of the plane"""


class PrismElement(Element3D):
    """A prism element is just an extrusion of a 2d shape."""

    element: Element2D
    amount: Mm
    taper: Degree

    def __init__(self, element: Element2D, amount: Mm, taper: Degree = 0) -> None:
        self.element = element
        self.amount = amount
        self.taper = taper

    @property
    @override
    def size(self) -> Vec3:
        size2d = self.element.size
        return Vec3(size2d.x, size2d.y, self.amount)

    @override
    def render(self, cut: bool = False) -> Piece:
        part = Location((0, 0, -self.amount / 2)) * extrude(
            self.element.sketch(), amount=self.amount, taper=self.taper
        )
        return Piece(part, cut)


class TubeElement(PrismElement):
    def __init__(self, base: Element2D, thickness: Mm, amount: Mm) -> None:
        super().__init__(RingElement(base, thickness), amount)


class BoxElement(PrismElement):
    """A box element is a 3d cuboid"""

    def __init__(self, dx: Mm, dy: Mm, dz: Mm) -> None:
        super().__init__(RectangleElement(dx, dy), dz)


class PlateElement(PrismElement):
    """A extruded RectangleElement"""

    def __init__(
        self,
        width: Mm,
        height: Mm,
        depth: Mm,
        corners: Mm | Corners | None = None,
        holes: HolePattern | None = None,
    ) -> None:
        super().__init__(RectangleElement(width, height, corners, holes), depth)


class CylinderElement(Element3D):
    """A cylinder element."""

    radius: Mm
    height: Mm

    def __init__(self, radius: Mm, height: Mm) -> None:
        self.radius = radius
        self.height = height

    @property
    @override
    def size(self) -> Vec3:
        return Vec3(2 * self.radius, 2 * self.radius, self.height)

    @override
    def render(self, cut: bool = False) -> Piece:
        return Piece(Cylinder(self.radius, self.height), cut)


class ConeElement(Element3D):
    """A cone element."""

    base_radius: Mm
    top_radius: Mm
    height: Mm

    def __init__(self, base_radius: Mm, top_radius: Mm, height: Mm) -> None:
        self.base_radius = base_radius
        self.top_radius = top_radius
        self.height = height

    @property
    @override
    def size(self) -> Vec3:
        max_radius = max(self.base_radius, self.top_radius)
        return Vec3(2 * max_radius, 2 * max_radius, self.height)

    @override
    def render(self, cut: bool = False) -> Piece:
        part = Location((0, 0, self.height / 2)) * Cone(
            self.base_radius, self.top_radius, self.height
        )
        return Piece(part, cut)


class StackElement(Element3D):
    """TODO: Make dir and align work features for this stack"""

    elements: Sequence[Element3D]

    def __init__(self, elements: Sequence[Element3D]) -> None:
        self.elements = elements

    @property
    @override
    def size(self) -> Vec3:
        return Vec3(
            max(e.size.x for e in self.elements),
            max(e.size.y for e in self.elements),
            sum(e.size.z for e in self.elements),
        )

    def render(self, cut: bool = False) -> Piece:
        size = self.size
        stack_dz = -size.z / 2
        stack = Part()
        for element in self.elements:
            stack += (
                Location((0, 0, stack_dz + element.size.z / 2)) * element.render(cut=False).part
            )
            stack_dz += element.size.z
        return Piece(stack, cut=cut)


class ImportElement(Element3D): 
    """An block formed from a BREP file or an STL file.
    
    BREP files are imported rapidly, while STL files are converted to a BREP model using the `Mesher` library which may take some time.
    STL files can be converted to a BREP model using the `import_stl.py` script.
    """

    BREP_SUFFIX: str = ".brep"
    STL_SUFFIX: str = ".stl"

    file: Path | None = None
    asset: str | None = None
    asset_folder: str | None = None

    def __init__(
        self,
        file: Path | None = None,
        asset: Path | None = None,
    ) -> None:
        """
        Initialize the ImportElement with the given path or asset name and optional parameters.

        Args:
            file (Path): The path to the BREP or STL file.
            asset (Path): The path to the asset to import.
        """
        if file is not None:
            if not file.exists():
                raise ValueError(f"Path does not exist: {file}")
            if not (file.suffix == self.BREP_SUFFIX or file.suffix == self.STL_SUFFIX):
                raise ValueError(f"Expected BREP or STL file, got {file.suffix}")
            self.file = file
        elif asset is not None:
            self.asset_folder = str(asset.parent)
            self.asset = asset.name
            if len(self.asset_folder) == 0:
                raise ValueError("asset must contain a folder")
        else:
            raise ValueError("Either path or asset must be provided")

    @cached_property
    def shape(self) -> Shape[TopoDS_Solid]:
        """
        Returns the shape of the part. Cached to avoid re-importing.
        """

        def convert_stl(path: Path) -> Shape[TopoDS_Solid]:
            # Import the STL file and center it around the bounding box
            importer = Mesher(unit=Unit.MM)
            full_mesh = importer.read(path)[0]
            center = Shape.combined_center([full_mesh], center_of=CenterOf.BOUNDING_BOX)
            centered_mesh = full_mesh.move(Location((-center.X, -center.Y, -center.Z)))
            return centered_mesh

        def import_path(path: Path) -> Shape[TopoDS_Solid]:
            match path.suffix:
                case self.STL_SUFFIX:
                    return convert_stl(path)
                case self.BREP_SUFFIX:
                    return import_brep(path)
                case _:
                    raise ValueError(f"Unexpected file suffix: {path.suffix}")

        if self.asset_folder is not None and self.asset is not None:
            # assets may be zipped when stored, so extract to a temporary directory
            with as_file(files(self.asset_folder) / self.asset) as asset_path:
                return import_path(asset_path)
        elif self.file is not None:
            return import_path(self.file)
        else:
            raise ValueError("No asset or path specified")

    @cached_property
    def size(self) -> Vec3:
        """
        Returns the size of the import. Cached to avoid recomputing.
        """
        bbox = self.shape.bounding_box()
        assert bbox.center() == Vector(0, 0, 0), f"Imported part is not centered: {bbox.center()}"
        return Vec3(bbox.size.X, bbox.size.Y, bbox.size.Z)

    @override
    def render(self, cut: bool = False) -> Piece:
        return Piece(self.shape.solid(), cut)

# def sketch_ring(element: Element2D, wall_thickness: Mm) -> Sketch:
#     """
#     Make a 2d ring from the element shape.
# 
#     Args:
#         element (Element2D): The shape of the ring.
#         wall_thickness (Mm): The thickness of the ring wall.
# 
#     Returns:
#         Part: The extruded ring of the basic shape.
#     """
#     inner = element.sketch()
#     outer = offset(inner, wall_thickness)
#     return Sketch(outer - inner)
# 
# 
# def extrude_tube(element: Element2D, wall_thickness: Mm, amount: Mm) -> Part:
#     """
#     Make a 3d tube from the element shape by outsetting the shape and extruding it along the Z axis.
# 
#     Args:
#         element (Element2D): The shape of the tube.
#         wall_thickness (Mm): The thickness of the tube wall.
#         amount (Mm): The amount to extrude the tube in the Z direction.
#     Returns:
#         Part: The extruded tube of the basic shape.
#     """
#     sketch = sketch_ring(element, wall_thickness)
#     return Location((0, 0, -amount / 2)) * extrude(sketch, amount)
# 
# 
# def extrude_sketch(sketch: Sketch, amount: Mm) -> Part:
#     """
#     Extrude a sketch along the Z axis.
# 
#     Args:
#         sketch (Sketch): The sketch to extrude.
#         amount (Mm): The amount to extrude the sketch in the Z direction.
#     Returns:
#         Part: The extruded sketch.
#     """
#     return Location((0, 0, -amount / 2)) * extrude(sketch, amount)
# 
# 
# def make_plate(size: Vec3, holes: HolePattern | None = None) -> Part:
#     """
#     Make a plate of the given size and fill pattern.
# 
#     Args:
#         size (VectorLike): The size of the plate.
#         holes (HolePattern, optional): The fill pattern of the plate. Defaults to SOLID.
# 
#     Returns:
#         Part: The extruded plate.
#     """
#     sketch = RectangleElement(size.x, size.y, holes=holes).sketch()
#     return Location((0, 0, -size.z / 2)) * extrude(sketch, size.z)
