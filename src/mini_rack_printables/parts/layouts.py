"""
Part Layouts

Place parts on a model's plate. Used by most models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from build123d import BuildPart, Part, add

from ..geometry import Rc
from ..selectors import Place
from .model_part import PlatePlanes, PartList, ModelPart, PartPiece
from .row_column_collection import RowColumnCollection
from ..dimensions import E


class PartLayout(ABC):
    """Base Layout class"""

    @abstractmethod
    def layout_parts(self, parts: PartList, plate_planes: PlatePlanes) -> list[PlatePlanes]:
        """
        Layout the 'parts' on the passed in 'plate' returning
        a list of sub plates for each passed in part.
        """
        pass

    @staticmethod
    def render_pieces(
        parts: PartList, plate_planes: PlatePlanes, layout: PartLayout
    ) -> list[PartPiece]:
        """
        Render all `parts` using the given `plate` and `layout` alogrithm.
        """
        pieces = []
        sub_plates = layout.layout_parts(parts, plate_planes)
        for part, _, _, index in RowColumnCollection(parts):
            part_pieces = part.render(sub_plates[index])
            pieces.extend(part_pieces)
        return pieces

    @staticmethod
    def assemble_pieces(to_part: Part, pieces: list[PartPiece]) -> Part:
        """
        Intersect `pieces` with `to_part` to create the final result.
        """
        with BuildPart() as result:
            add(to_part)
            for piece in pieces:
                add(piece.part, mode=piece.mode)
        assert result.part is not None
        return result.part


class RowLayout(PartLayout):
    """
    Layout each row independently according to the part's desired size. If desired size
    is does not fill the plate's width, then allocate space according to part's desires.
    """

    def __init__(
        self,
        equal_heights: bool = False,
        row_heights: list[float] | None = None,
        equal_widths: bool = False,
        align: Place = Place.CENTER,
        spacing: float = 0,
    ):
        """
        Args:
            equal_row_heights (bool): if True, all rows will have the same height. Overrides parts' desired heights.
            row_heights (list[float] | None): exact height for each row. If None, uses parts' desired heights.
            align (Place): how to align each cell
            spacing (float): Spacing around each cell.
        """
        if row_heights is not None and equal_heights:
            raise ValueError("Cannot set both row_heights and equal_row_heights")
        self.equal_heights = equal_heights
        self.row_heights = row_heights
        self.equal_widths = equal_widths
        self.align = align
        self.spacing = spacing

    def _layout_vert(
        self,
        coll: RowColumnCollection[ModelPart],
        m: MeasuredRowsColumns,
        plate_planes: PlatePlanes,
    ) -> list[float]:
        """Calculate the vertical heights of rows in the top-to-bottom direction"""
        s = self.spacing
        rc = coll.row_count
        plate_height = plate_planes.bounds.size.Y
        # Calculate the excess space to distribute and how many rows can expand
        total_height = sum(m.min_y)
        expand_count = sum(1 for more in m.more_y if more)
        excess = plate_height - total_height - s * (rc + 1)
        if excess < 0:
            raise ValueError(
                f"Minimum total height {total_height} is larger than available plate height {plate_height}"
            )

        if self.row_heights:
            # use caller-defined row heights
            if len(self.row_heights) != rc:
                raise ValueError("row_heights must have the same length as the number of rows")
            specified_height = sum(self.row_heights) + (rc + 1) * s
            if not (plate_height - E <= specified_height <= plate_height + E):
                raise ValueError(
                    f"Sum of specified row_heights {specified_height} does not equal the plate height {plate_height}"
                )
            return self.row_heights
        if self.equal_heights:
            # distribute plate height evenly between rows
            return [(plate_height - s * (rc + 1)) / rc] * rc
        if expand_count == 0:
            # distribute excess space evenly between all rows
            return [h + (excess / rc) for h in m.min_y]

        # distribute excess space evenly between expanding rows
        def expanded_height(row_idx: int) -> float:
            h = m.min_y[row_idx]
            return h + (excess / expand_count) if m.more_y[row_idx] else h

        return [expanded_height(i) for i in range(rc)]

    def layout_parts(self, parts: PartList, plate_planes: PlatePlanes) -> list[PlatePlanes]:
        coll = RowColumnCollection(parts)
        m = MeasuredRowsColumns.measure_parts(coll)
        s = self.spacing

        def layout_one(parts: list[ModelPart]) -> list[float]:
            """Calculate the horizontal widths of cells of one row the left-to-right direction"""
            plate_width = plate_planes.bounds.size.X
            cc = len(parts)
            total_width = sum(part.desired_size().min_size.X for part in parts)
            expand_count = sum(1 for part in parts if part.desired_size().more_x)
            excess = plate_width - total_width - s * (cc + 1)
            if excess < 0:
                raise ValueError(
                    f"Minimum total width ({total_width}) is larger than plate width ({plate_width})."
                )
            if self.equal_widths:
                return [(plate_width - s * (cc + 1)) / cc] * cc
            if expand_count == 0:
                # distribute excess space evenly between all columns
                return [part.desired_size().min_size.X + (excess / cc) for part in parts]

            # distribute excess space evenly between expanding columns
            def expanded_width(part: ModelPart) -> float:
                ds = part.desired_size()
                return ds.min_size.X + (excess / expand_count) if ds.more_x else ds.min_size.X

            return [expanded_width(part) for part in parts]

        # Iterate over rows and columns to form sub_plates for each part.
        # Increment top and left with spacing to position each sub_plate correctly.
        result: list[PlatePlanes] = []
        front = plate_planes.bounds.front
        back = plate_planes.bounds.back
        left = plate_planes.bounds.left + s
        top = plate_planes.bounds.top - s
        for row, row_height in zip(coll.rows, self._layout_vert(coll, m, plate_planes)):
            bottom = top - row_height
            for col_idx, item_width in enumerate(layout_one(row)):
                right = left + item_width

                part = row[col_idx]
                bounds = Rc.from_edges(left, right, bottom, top)
                bounds_bx = bounds.form_bx(front, back)
                part_rc = Rc(part.desired_size().min_size, bounds.shift)
                origin_offset = part_rc.bounds_shift(bounds, self.align)
                result.append(PlatePlanes(bounds_bx, origin_offset))

                left = right + s
            top = bottom - s
            left = plate_planes.bounds.left + s

        return result


class GridLayout(RowLayout):
    """
    Layout the rows and columns of parts according to the parts desired and minimum size. If desired size
    is does not fill a row or column, then allocated space evenly. The layout so that all rows and columns
    to align.
    """

    def __init__(
        self,
        row_heights: list[float] | None = None,
        equal_heights: bool = False,
        col_widths: list[float] | None = None,
        equal_widths: bool = False,
        align: Place = Place.CENTER,
        spacing: float = 0,
    ):
        super().__init__(equal_heights, row_heights, equal_widths, align, spacing)
        self.col_widths = col_widths

    def layout_parts(self, parts: PartList, plate_planes: PlatePlanes) -> list[PlatePlanes]:
        coll = RowColumnCollection(parts)
        m = MeasuredRowsColumns.measure_parts(coll)
        s = self.spacing

        def layout_horiz() -> list[float]:
            """Calculate the horizontal widths of cells of columns in the left-to-right direction"""
            cc = coll.col_count
            plate_width = plate_planes.bounds.size.X

            # Calculate the excess space to distribute and how many columns can expand
            total_width = sum(m.min_x)
            expand_count = sum(1 for more in m.more_x if more)
            excess = plate_width - total_width - s * (cc + 1)
            if excess < 0:
                raise ValueError(
                    f"Minimum total width {total_width} is larger than available space"
                )

            if self.col_widths:
                # use caller-defined column widths, check the supplied widths
                if len(self.col_widths) != cc:
                    raise ValueError(
                        "col_widths must have the same length as the number of columns"
                    )
                specified_width = sum(self.col_widths) + (cc + 1) * s
                if not (plate_width - E <= specified_width <= plate_width + E):
                    raise ValueError(
                        f"Sum of specified col_widths {specified_width} does not equal the plate width {plate_width}"
                    )
                return self.col_widths
            if self.equal_widths:
                # distribute plate widths evenly between columns
                return [(plate_width - s * (cc + 1)) / cc] * cc
            if expand_count == 0:
                # distribute excess space evenly between all columns
                return [w + (excess / cc) for w in m.min_x]

            # distribute excess space evenly between expanding columns
            def expanded_width(col_idx: int) -> float:
                w = m.min_x[col_idx]
                return w + (excess / expand_count) if m.more_x[col_idx] else w

            return [expanded_width(i) for i in range(cc)]

        result: list[PlatePlanes] = []
        front = plate_planes.bounds.front
        back = plate_planes.bounds.back
        left = plate_planes.bounds.left + s
        top = plate_planes.bounds.top - s
        vert_layout = self._layout_vert(coll, m, plate_planes)
        horz_layout = layout_horiz()
        for row_idx, row_height in enumerate(vert_layout):
            bottom = top - row_height
            for col_idx, item_width in enumerate(horz_layout):
                right = left + item_width

                part = coll.get_item(row_idx, col_idx)
                if part is not None:
                    bounds = Rc.from_edges(left, right, bottom, top)
                    bounds_bx = bounds.form_bx(front, back)
                    part_rc = Rc(part.desired_size().min_size, bounds.shift)
                    origin_offset = part_rc.bounds_shift(bounds, self.align)
                    result.append(PlatePlanes(bounds_bx, origin_offset))

                left = right + s
            top = bottom - s
            left = plate_planes.bounds.left + s
        return result


@dataclass(frozen=True)
class MeasuredRowsColumns:
    """Holds the measured rows and columns of a layout collection"""

    min_x: list[float]
    more_x: list[bool]
    min_y: list[float]
    more_y: list[bool]

    @classmethod
    def measure_parts(cls, parts: RowColumnCollection[ModelPart]) -> MeasuredRowsColumns:
        min_x = [
            max(
                part.desired_size().min_size.X if part is not None else 0
                for part in parts.get_column(col_idx)
            )
            for col_idx in range(parts.col_count)
        ]
        min_y = [
            max(part.desired_size().min_size.Y for part in parts.get_row(row_idx))
            for row_idx in range(parts.row_count)
        ]
        more_x = [
            any(
                part.desired_size().more_x if part is not None else False
                for part in parts.get_column(col_idx)
            )
            for col_idx in range(parts.col_count)
        ]
        more_y = [
            any(part.desired_size().more_y for part in parts.get_row(row_idx))
            for row_idx in range(parts.row_count)
        ]

        return cls(
            min_x=min_x,
            more_x=more_x,
            min_y=min_y,
            more_y=more_y,
        )
