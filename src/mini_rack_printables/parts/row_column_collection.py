"""
A Collection of either list of items or a list of lists of items. In all cases, the collection can
be treated as a 2d row-column collection.
"""

from typing import cast


class RowsColumnsIterator[T]:
    """
    An iterator over the items in a RowsColumnsCollection by row and then column.
    Returns the item, row, column, and index of each item.
    """

    def __init__(self, collection: "RowsColumnsCollection[T]") -> None:
        self.collection = collection
        self.row = 0
        self.col = 0
        self.index = 0

    def __iter__(self) -> RowsColumnsIterator[T]:
        return self

    def __next__(self) -> tuple[T, int, int, int]:
        if self.row >= self.collection.row_count:
            raise StopIteration
        row_items = self.collection.get_row(self.row)
        if self.col >= len(row_items):
            self.row += 1
            self.col = 0
        item = row_items[self.col]
        yield item, self.row, self.col, self.index
        self.col += 1
        self.index += 1


class RowsColumnsCollection[T]:
    """
    A Collection of either list of items or a list of lists of items. In all cases, the collection can 
    be treated as a 2d row-column collection. 
    The array may be sparse (e.g. some rows may have fewer columns) or full (e.g. all rows have the same number of columns).
    """
    rows: list[list[T]]
    """The rows of the collection."""
    row_count: int
    """The number of rows in the collection."""
    col_count: int
    """The number of columns in the collection."""
    is_full: bool
    """Whether the collection is full with all row containing the same number of columns."""
    length: int
    """The total number of items in the collection."""

    def __init__(self, items: list[T] | list[list[T]]) -> None:
        """
        Initialize a sparse or full 2D collection of items.
        """
        if len(items) == 0:
            self.row_count = 0
            self.col_count = 0
            self.is_full = True
            self.length = 0
            self.rows = []
        elif isinstance(items[0], type(T)):
            self.row_count = 1
            self.col_count = len(items)
            self.is_full = True
            self.length = len(items)
            self.rows = [items]
        else:
            assert isinstance(items[0], list)
            self.rows = items
            self.row_count = len(items)
            self.col_count = max(len(row) for row in items if isinstance(row, list))
            self.is_full = all(
                len(row) == self.col_count for row in items if isinstance(row, list)
            )
            self.length = sum(len(row) for row in items if isinstance(row, list))

    def __iter__(self) -> RowsColumnsIterator[T]:
        """Return an iterator over the rows and columns of this collection."""
        return RowsColumnsIterator(self)

    def __len__(self) -> int:
        """Return the total number of items in this collection."""
        return self.length

    def get_item(self, row: int, col: int) -> T:
        """Return the item at the given `row` and `col`."""
        if row >= self.row_count or col >= self.col_count:
            raise IndexError("row or col is out of bounds")
        row_items = self.get_row(row)
        if col >= len(row_items):
            raise IndexError("col is out of bounds")
        return row_items[col]

    def get_row(self, row: int) -> list[T]:
        """Return the row at the given `row`."""
        if row >= self.row_count:
            raise IndexError("row is out of bounds")
        return self.rows[row]

    def get_column(self, col: int) -> list[T | None]:
        """Return the column at the given `col`. If the collection is sparse, `None` is returned for missing items."""
        if col >= self.col_count:
            raise IndexError("col is out of bounds")
        return [row[col] if col < len(row) else None for row in self.rows]

    def apply(self, func: Callable[[T], T]) -> None:
        for row in self.rows:
            for i, item in enumerate(row):
                row[i] = func(item)
