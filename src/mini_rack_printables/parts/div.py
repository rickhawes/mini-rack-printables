from typing import TypeAlias, Sequence
from .model_part import ModelPart, PartTreeNode
from ..geometry import RcAlignment, Dir, Rc, convert_to_3d
from build123d import Vector, Location


DivSize: TypeAlias = str | float | int
DivSizes: TypeAlias = Sequence[DivSize]


class Div(ModelPart):
    """
    A div is used to layout a section of a plate by evenly dividing the plate in either
    the horizontal (default) or verticle direction.

    Attributes:
        parts: The parts of the div.
        dir: The direction that the div's sections are laid out.
        sizes: The sizes of the div's sections.
    """

    dir: Dir
    sizes: list[DivSize]
    parts: list[ModelPart]

    AUTO = "*"

    def __init__(
        self,
        parts: list[ModelPart],
        dir: Dir = Dir.HORIZONTAL,
        name: str = "Div",
        sizes: list[DivSize] = [AUTO],
        align: Vector = RcAlignment.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0,
    ):
        """
        Initialize a Div feature

        Args:
            parts: The parts of the div.
            dir: The direction of the sections.
            sizes: The sizes of the sections.
            name: The name of the div.
            align: Alignment within a parent div section.
            shift: Shift within a parent div section.
            padding: Padding within a parent div section.
        """
        super().__init__(name, align, shift, padding)
        self.dir = dir
        self.sizes = sizes
        self.parts = parts

    def layout_size(self, plate_size: Vector) -> Vector:
        return Vector(plate_size.X, plate_size.Y)

    def render(self, plate_size: Vector) -> list[PartTreeNode]:
        """
        Render the div feature by dividing the plate into sections and rendering each feature.
        """
        extended_sizes = Div.extend_sizes(self.sizes, len(self.parts))
        sections_rc = Div.divide_by_sizes(Rc(plate_size), extended_sizes, self.dir)
        nodes = []
        for i in range(len(self.parts)):
            shift = Div.layout_part(self.parts[i], sections_rc[i])
            part_nodes = self.parts[i].render(convert_to_3d(sections_rc[i].size, plate_size.Z))
            nodes += [
                PartTreeNode(
                    name=node.name,
                    part=node.part,
                    loc=Location(shift) * node.loc,
                    mode=node.mode,
                )
                for node in part_nodes
            ]
        return nodes

    @staticmethod
    def is_valid_sizes(sizes: DivSizes) -> bool:
        """
        Check if the list of sizes is valid.
        """
        for s in sizes:
            if isinstance(s, float) or isinstance(s, int):
                if float(s) <= 0:
                    return False
            elif s != Div.AUTO:
                return False
        return True

    @staticmethod
    def extend_sizes(sizes: DivSizes, num_parts: int) -> DivSizes:
        """
        Extend the size array to match the parts (i.e. one size for each part)
        """
        last_size = sizes[-1]
        sizes_needed = num_parts - len(sizes)
        if sizes_needed > 0:
            return list(sizes) + [last_size] * sizes_needed
        else:
            return sizes

    @staticmethod
    def sum_static(sizes: DivSizes) -> float:
        """
        Sum the static sizes (non-AUTO values) in the given list.
        """
        return sum([s for s in sizes if s != Div.AUTO])

    @staticmethod
    def count_auto(sizes: DivSizes) -> int:
        """
        Sum the static sizes (non-AUTO values) in the given list.
        """
        return sum([1 for s in sizes if s == Div.AUTO])

    @staticmethod
    def fill_in_sizes(sizes: DivSizes, bounding_size: Vector, dir=Dir.HORIZONTAL) -> list[float]:
        """
        Replace "str sizes with their float values,
        filling in auto sizes ("*") with the calculated size based on the bounding size.
        """
        assert Div.is_valid_sizes(sizes)
        r_size = bounding_size.X if dir == Dir.HORIZONTAL else bounding_size.Y
        total_auto_size = r_size - Div.sum_static(sizes)
        assert total_auto_size >= 0, "static sizes must be less than the r size"
        num_auto = Div.count_auto(sizes)
        if num_auto == 0:
            return [float(s) for s in sizes]
        else:
            auto_size = total_auto_size / num_auto
            return [auto_size if s == Div.AUTO else float(s) for s in sizes]

    @staticmethod
    def divide_by_sizes(r: Rc, sizes: DivSizes = [AUTO], dir=Dir.HORIZONTAL) -> list[Rc]:
        """
        Divide a RC based on the given sizes and direction.
        """
        adjusted_sizes: list[float] = Div.fill_in_sizes(sizes, r.size, dir)
        result: list[Rc] = []
        remaining = r
        for i, s in enumerate(adjusted_sizes):
            if i == len(sizes) - 1:
                result.append(remaining)
            else:
                splits = remaining.split(s, dir)
                result.append(splits[0])
                remaining = splits[1]
        return result

    @staticmethod
    def layout_part(part: ModelPart, bounding: Rc) -> Vector:
        """
        Place a part within the given RC, returning the shift vector.
        """
        layout_rc = Rc(part.layout_size(bounding.size))
        layout_with_padding = layout_rc.apply_padding(part.padding)
        aligned_shift = layout_with_padding.alignment_shift(bounding, part.align)
        return aligned_shift + part.shift
