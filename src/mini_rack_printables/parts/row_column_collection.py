"""
A Collection of either list of items or a list of lists of items. In all cases, the collection can
be treated as a 2d row-column collection.
"""

from typing import cast, Iterator, Callable


class RowColumnCollection[T]:
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
        elif not isinstance(items[0], list):
            self.row_count = 1
            self.col_count = len(items)
            self.is_full = True
            self.length = len(items)
            self.rows = [cast(list[T], items)]
        else:
            assert isinstance(items[0], list)
            self.rows = cast(list[list[T]], items)
            self.row_count = len(items)
            self.col_count = max(len(row) for row in items if isinstance(row, list))
            self.is_full = all(
                len(row) == self.col_count for row in items if isinstance(row, list)
            )
            self.length = sum(len(row) for row in items if isinstance(row, list))

    def __iter__(self) -> Iterator[tuple[T, int, int, int]]:
        """Return an iterator over the rows and columns of this collection."""
        row, col, index = 0, 0, 0
        while row < self.row_count:
            row_items = self.get_row(row)
            item = row_items[col]
            yield item, row, col, index
            col += 1
            index += 1
            if col >= len(row_items):
                row += 1
                col = 0

    def __len__(self) -> int:
        """Return the total number of items in this collection."""
        return self.length

    def get_item(self, row: int, col: int) -> T | None:
        """Return the item at the given `row` and `col`."""
        if row >= self.row_count or col >= self.col_count:
            raise IndexError("row or col is out of bounds")
        row_items = self.get_row(row)
        return row_items[col] if col < len(row_items) else None

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

    def apply[U](self, func: Callable[[T], U]) -> RowColumnCollection[U]:
        """Apply the given function to each item in this collection, returning a new collection with the results, keeping the shape of the this collection."""
        new_rows: list[list[U]] = [[func(item) for item in row] for row in self.rows]
        return RowColumnCollection[U](new_rows)

    def flatten(self) -> list[T]:
        """Return a flattened list of all items in this collection."""
        return [item for row in self.rows for item in row]
