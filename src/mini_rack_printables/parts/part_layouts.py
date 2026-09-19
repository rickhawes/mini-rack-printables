"""
Part Layouts

Layouts place parts on a model's plate
"""

from build123d import Vector
from abc import ABC, abstractmethod

from .model_part import Plate, PartList, ModelPart
from .row_column_collection import RowsColumnsCollection
from ..selectors import Place
from ..dimensions import MIN_SPACING


class PartLayout(ABC):
    """Base Layout class"""

    @abstractmethod
    def layout_parts(self, parts: PartList, plate: Plate) -> list[Plate]:
        """
        Layout the 'parts' on the passed in 'plate' returning
        a list of sub plates for each passed in part.
        """
        pass

    @dataclass
    class Measured:
        row_heights: list[float]
        row_expanding: list[bool]
        col_widths: list[float]
        col_expanding: list[bool]

    def _measure_parts(self, coll: RowsColumnsCollection) -> PartLayout.Measured:
        coll_measurements = RowsColumnsCollection[D]]
            
            

        return PartLayout.Measured(row_heights, row_expanding, col_widths, col_expanding)

class RowLayout(PartLayout):
    """
    Layout a row of parts according to the parts desired and minimum size. If desired size
    is does not fill the row, then allocated space evenly. The layout each row independently.
    """

    def __init__(
        self,
        row_heights: list[float] | None = None,
        align: Place = Place.CENTER,
        spacing: float = MIN_SPACING,
    ):
        """

        Args:
            row_heights (list[float]): exact height for each row.
            align (Place): how to align each cell
            spacing (float): spacing between cells and around each cell.
        """
        self.row_heights = row_heights
        self.align = align
        self.spacing = spacing


    def layout_parts(self, parts: PartList, plate: Plate) -> list[Plate]:
        coll = RowsColumnsCollection(parts)
        # measure the parts to determine row heights and column widths

        def layout_rows() -> list[float]:
            if self.row_heights:
                return self.row_heights
            row_desires = [
                (
                    max(part.layout_size().min_size.Y for part in coll.get_row(row_idx)),
                    any(part.layout_size().expand for part in coll.get_row(row_idx)),
                )
                for row_idx in range(coll.row_count)
            ]
            total_row_height = sum(row_desires[0])
            if total_row_height > plate.size.Y:
                raise ValueError(
                    f"Total row min-height exceeds plate size: {total_row_height} > {plate.size.Y}"
                )
            expanding_rows_count = sum(1 for row_desire in row_desires if row_desire[1])
            if expanding_rows_count == 0:
                padding = (plate.size.Y - total_row_height) / coll.row_count
                return [row_desire[0] + padding for row_desire in row_desires]
            else:
                padding = (plate.size.Y - total_row_height) / expanding_rows_count
                return [
                    row_desire[0] + padding if row_desire[1] else row_desire[0]
                    for row_desire in row_desires
                ]

        def layout_one_row(parts: list[ModelPart]) -> list[float]:
            min_width = max(part.layout_size().min_size.X for part in parts)
            expand_count = sum(1 for part in parts if part.layout_size().expand)
            if min_width > plate.size.X:
                raise ValueError(f"Part width exceeds plate size: {min_width} > {plate.size.X}")
            if expand_count == 0:
                padding = (plate.size.X - min_width) / coll.col_count
                return [part.layout_size().min_size.X + padding for part in parts]
            else:
                padding = (plate.size.X - min_width) / expand_count
                return [
                    part.layout_size().min_size.X + padding
                    if part.layout_size().expand
                    else part.layout_size().min_size.X
                    for part in parts
                ]

        return []


class GridLayout(PartLayout):
    """
    Layout the rows and columns of parts according to the parts desired and minimum size. If desired size
    is does not fill a row or column, then allocated space evenly. The layout so that all rows and columns
    to align.
    """

    def __init__(
        self,
        row_heights: list[float] | None = None,
        col_widths: list[float] | None = None,
        align: Place = Place.CENTER,
        spacing: float = MIN_SPACING,
    ):
        self.row_heights = row_heights
        self.col_widths = col_widths
        self.align = align
        self.spacing = spacing

    def layout_parts(self, parts: PartList, plate: Plate) -> list[Plate]:
        raise NotImplementedError
