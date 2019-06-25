"""Tableread module to write a text file from a Python object."""
import io
import os
from typing import List, Tuple


RowData = List[dict]


class SimpleRSTTableWriteable(object):
    """Single rST table object to be written."""

    divider_char = "="
    title_marker = "~"

    def __init__(self, title: str, row_data: RowData):
        self.title = title
        self._headers = list(row_data[0].keys())
        self.col_widths = self._col_widths(row_data)
        self.col_mappings = list(zip(self._headers, self.col_widths))
        self.rows = self._dict_to_lines(row_data)

    def _format_row(self, row: dict):
        return "  ".join(
            ["{:{c}}".format(row.get(k, ""), c=c) for k, c in self.col_mappings]
        )

    def _dict_to_lines(self, row_data: RowData):
        return [self._format_row(row) for row in row_data]

    def _col_widths(self, row_data: RowData):
        return [
            max(len(col), *[len(str(row.get(col, ""))) for row in row_data])
            for col in self._headers
        ]

    @property
    def headers(self):
        """Headers for the table, formatted as a spaced string."""
        return "  ".join(["{:{c}}".format(k, c=c) for k, c in self.col_mappings])

    @property
    def divider(self):
        """Format divider row as a spaced string."""
        return "  ".join([self.divider_char * x for x in self.col_widths])

    def write_table(self, writer: io.TextIOBase):
        """Write table out to file using the provided writer.

        Args:
            writer: file-like object to be written to
        """
        self._write_title(writer)
        self._write_headers(writer)
        for row in self.rows:
            self._write(writer, row)
        self._write(writer, self.divider)

    def _write_title(self, writer: io.TextIOBase):
        self._write(writer, self.title)
        self._write(writer, self.title_marker * len(self.title))
        self._write(writer, "")

    def _write_headers(self, writer: io.TextIOBase):
        self._write(writer, self.divider)
        self._write(writer, self.headers)
        self._write(writer, self.divider)

    def _write(self, writer: io.TextIOBase, string: str):
        writer.write("{}\n".format(string))


class SimpleRSTWriter(object):
    """Write a .rst file from a list of tables."""

    def __init__(self, file_path: str, *tables: Tuple[str, RowData]):
        """Accept a list of table information and write to file.

        Args:
            file_path: the path to write the output file
            tables: Each a tuple of table title (str) and list of row dicts
        """
        self.file_path = file_path
        self.tables = [SimpleRSTTableWriteable(title, rows) for title, rows in tables]

    def write_tables(self):
        """Write provided tables out to .rst file."""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        dirname = os.path.dirname(self.file_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(self.file_path, "a") as writer:
            for idx, table in enumerate(self.tables):
                if idx:
                    writer.write("\n")
                    writer.write("\n")
                table.write_table(writer)
