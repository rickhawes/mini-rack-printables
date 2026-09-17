"""
Part Layouts

Layouts place parts on a model's surface
"""

from build123d import Vector
from abc import ABC, abstractmethod

from ..parts.model_part import Plate, PartList
from ..selectors import Place


class PartLayout(ABC):
    @abstractmethod
    def layout_parts(self, parts: PartList, plate: Plate) -> list[Plate]:
        pass


class RowLayout(PartLayout):
    def __init__(
        self,
        row_spacing: list[float] | None = None,
        align: Place = Place.CENTER,
        shift: Vector = Vector(0, 0, 0),
        padding: float = 0.0,
    ):
        self.row_spacing = row_spacing
        self.align = align
        self.shift = shift
        self.padding = padding

    def layout_parts(self, parts: PartList, plate: Plate) -> list[Plate]:
        raise NotImplementedError


class GridLayout(PartLayout):
    def __init__(
        self,
        row_spacing: list[float] | None = None,
        col_spacing: list[float] | None = None,
        align: Place = Place.CENTER,
        shift: Vector = Vector(0, 0, 0),
        padding: float = 0.0,
    ):
        self.row_spacing = row_spacing
        self.col_spacing = col_spacing
        self.align = align
        self.shift = shift
        self.padding = padding

    def layout_parts(self, parts: PartList, plate: Plate) -> list[Plate]:
        raise NotImplementedError
