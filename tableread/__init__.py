"""Tableread package to read a text file table into a Python object."""

import os
from collections import OrderedDict

from itertools import filterfalse
from operator import attrgetter

import attr


def _safe_name(name):
    return name.replace(" ", "_").replace(".", "_").lower()


def get_specific_attr_matcher(key, value):
    """
    Check if a given attribute value matches the expected value.

    Args:
        key (str): the name of the attribute to check
        value (str): the expected string value

    Returns:
        function: a checker that will accept an object
        and return True if the attribute value matches, or False if not.

    """
    return lambda x: getattr(x, key).lower() == value.lower()


def safe_list_index(a_list, index_value, default=None):
    """
    Return the value at the given index, or a default if index does not exist.

    Args:
        a_list (list): the list to be indexed
        index_value (int): the desired index position from the list
        default (any): the default value to return if the given index does not exist

    Returns:
        any: the value at the list index position or the default

    """
    if index_value < 0:
        return default
    try:
        return a_list[index_value]
    except IndexError:
        return default


class BaseRSTDataObject(object):
    """Base Class for RST Table Data handling."""

    column_divider_char = " "
    header_divider = "="
    # The full set of potential ReStructuredText section markers is sourced from
    # http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#sections
    header_markers = set(r'!"#$%&\'()*+,-./:;<=>?@[]^_`{|}~')
    column_default_separator = "="
    comment_char = "#"
    data_format = None

    def __init__(self):
        self.data = self.data_format()

    def __len__(self):
        """Get the length of the underlying data."""
        return len(self.data)

    def __iter__(self):
        """Iterate over underlying data."""
        for data in self.data:
            yield data

    def __getitem__(self, key):
        """Get the value of the given key from the data."""
        return self.data[key]

    def _is_divider_row(self, row):
        if not row.startswith(self.header_divider):
            return False
        return self.header_divider in row and set(row) <= {
            self.column_divider_char,
            self.header_divider,
            " ",
        }


class SimpleRSTTable(BaseRSTDataObject):
    """Represent a single table from a RST file."""

    data_format = list

    def __init__(self, divider_row, header, rows):
        """
        Build a table from the text string parts.

        Args:
            divider_row (str): the row above or below the table headers,
                consisting solely of "=" and spaces,
                that delineates the column boundaries.
            header (str): the column header row
            rows (List[str]): the rows within the table containing data
        """
        super(SimpleRSTTable, self).__init__()
        self._header = header
        self._rows = rows
        self._column_spans = self._build_column_spans(divider_row)
        self._row_length = len(divider_row)
        self._build_data()

    @classmethod
    def from_data(cls, data):
        """Given data, build a SimpleRSTTable object."""
        table = cls.__new__(cls)
        table.data = list(data)
        return table

    def _build_column_spans(self, divider_row):
        # remove any trailing whitespace from the end of the row
        divider_row = divider_row.rstrip()
        column_spans = []
        start = 0
        next_break = divider_row.find(self.column_divider_char, start)
        while next_break != -1:
            column_spans.append((start, next_break))
            start = divider_row.find(self.header_divider, next_break)
            next_break = divider_row.find(self.column_divider_char, start)
        column_spans.append((start, None))
        return column_spans

    def _stop_checker(self, row):
        return self._is_divider_row(row)

    def _row_splitter(self, row):
        assert self._column_spans, "Column spans not defined!"
        # first, pad the row with spaces in case end columns are left empty
        row = "{row:{length}}".format(row=row, length=self._row_length)
        # then, find the columns in the row
        columns = []
        for (col_start, col_stop) in self._column_spans:
            column = row[col_start:col_stop]
            columns.append(column.strip().replace("..", ""))
        return columns

    def _set_header_names_and_defaults(self, fields):
        name_sets = [x.split(self.column_default_separator, 1) for x in fields]
        self.fields = [_safe_name(x[0].strip()) for x in name_sets]
        self.defaults = [x[1].strip() if len(x) > 1 else "" for x in name_sets]

    def _build_data(self):
        self._set_header_names_and_defaults(self._row_splitter(self._header))
        row_class = attr.make_class("Row", self.fields, hash=True)
        for row in self._rows:
            if self._stop_checker(row):
                break
            if "\t" in row:
                raise TabError("Tabs are not supported in tables - use spaces only!")
            row = row.split(" {} ".format(self.comment_char))[0]
            if row.count(self.column_divider_char) or len(self._column_spans) == 1:
                row = self._row_splitter(row)
                message = "Row '{}' does not match field list '{}' length."
                assert len(row) == len(self.fields), message.format(row, self.fields)
                row_data = (
                    value if value else default
                    for default, value in zip(self.defaults, row)
                )
                self.data.append(row_class(*row_data))

    def _filter_data(self, data, filter_kwargs, filter_func):
        filters = [
            v if callable(v) else get_specific_attr_matcher(k, v)
            for k, v in filter_kwargs.items()
        ]
        data = filter_func(lambda x: all(f(x) for f in filters), data)
        return self.__class__.from_data(data)

    def matches_all(self, **kwargs):
        """
        Filter data for a positive match to conditions.

        Given a set of key/value filters,
        returns a new TableRead object with the filtered data,
        that can be iterated over.
        Kwarg values may be a simple value (str, int)
        or a function that returns a boolean.

        Note: When filtering both keys and values are **not** case sensitive.
        """
        return self._filter_data(self.data, kwargs, filter)

    def exclude_by(self, **kwargs):
        """
        Filter data to exclude items matching conditions.

        Given a set of key/value filters,
        returns a new TableRead object without the matching data,
        that can be iterated over.
        Kwarg values may be a simple value (str, int)
        or a function that returns a boolean.

        Note: When filtering both keys and values are **not** case sensitive.
        """
        return self._filter_data(self.data, kwargs, filterfalse)

    def get_fields(self, *fields):
        """
        Get only specified fields from data.

        Given a set of fields, returns a list of those field values from each entry.
        A single field will return a list of values,
        Multiple fields will return a list of tuples of values.
        """
        return list(map(attrgetter(*fields), self.data))


class SimpleRSTReader(BaseRSTDataObject):
    """Represent all tables found in a RST file."""

    data_format = OrderedDict

    def __init__(self, rst_source):
        """
        Determine from where to parse RST content and then parse it.

        Args:
            rst_source (str): The source of the RST content to parse.
                This can either be a file path with a ``.rst`` extension,
                or a string containing the RST content.
        """
        super(SimpleRSTReader, self).__init__()
        rst_string = rst_source
        if rst_source.lower().endswith(".rst"):
            rst_string = self._read_file(rst_source)
        self._parse(rst_string)
        assert self.data, "No tables could be parsed from the RST source."

    @staticmethod
    def _read_file(file_path):
        assert os.path.exists(file_path), "File not found: {}".format(file_path)
        with open(file_path, "r") as rst_fo:
            return rst_fo.read()

    @property
    def first(self):
        """Return the first table found in the document."""
        return list(self.data.values())[0]

    def _is_header_underline(self, row):
        return any((set(row) == set(x) for x in self.header_markers))

    def _name_if_header(self, four_rows):
        above, header, below, tail = four_rows
        # Row below potential section header must be an underline row
        if not self._is_header_underline(below):
            return None
        # Row above should be an matching overline or empty
        if above and not above == below:
            return None
        # the line below the underline should be empty
        # (this condition ensures we don't take a table header as a section name)
        if tail:
            return None
        return header

    def _table_name(self, section_header):
        section_header = section_header or "Default"
        if section_header not in self.data.keys():
            return section_header
        name_number = 2
        while True:
            name = "{}_{}".format(section_header, name_number)
            if name not in self.data.keys():
                return name
            name_number += 1

    def _parse(self, rst_string):
        text_lines = rst_string.split("\n")
        section_header_cursor = None
        i = 0
        while i < len(text_lines) - 1:
            sliding_window = [
                safe_list_index(text_lines, idx, default="")
                for idx in range(i - 1, i + 3)
            ]
            header_check = self._name_if_header(sliding_window)
            if header_check:
                section_header_cursor = header_check
                # skip past the section header AND the underline row
                i += 2
                continue
            if self._is_divider_row(text_lines[i]):
                header, rows = self._get_header_and_rows(text_lines[i:])
                table_name = self._table_name(section_header_cursor)
                self.data[table_name] = SimpleRSTTable(text_lines[i], header, rows)
                # The extra 4 rows 'skipped' are for the 3 divider rows and the header
                i += len(rows) + 4
            i += 1

    def _get_header_and_rows(self, text_lines):
        header, rows = None, None
        # find the header
        for i in range(len(text_lines)):
            if self._is_divider_row(text_lines[i]):
                assert (
                    text_lines[i] == text_lines[i + 2]
                ), "Column divider rows do not match!"
                header, rows = text_lines[i + 1], text_lines[i + 3 :]
                break
        # truncate remaining rows to just table contents
        for i in range(len(rows)):
            if self._is_divider_row(rows[i]):
                rows = rows[:i]
                break
        return header, rows

    @property
    def tables(self):
        """Get the list of table names found in the document."""
        return list(self.data.keys())
