TableRead
=========

TableRead is a script designed to read reStructredText (reST) `simple tables`_ from a file and convert them into Python objects.


Quickstart
----------

Say you have a simple table like this located in a ``./example.rst``::

    ++++++++++++
    Damage Doers
    ++++++++++++

    ======  ===  ==============
    Name    Age  Favorite Color
    ======  ===  ==============
    Mookie  26   Red
    Andrew  24   Red
    JD      31   Red
    Xander  26   Red
    ======  ===  ==============

Here are a few useful things you can do with that table::

    >>> from tableread import SimpleRSTReader
    >>>
    >>> reader = SimpleRSTReader("./example.rst")
    >>> reader.tables
    ['Damage Doers']
    >>>
    >>> table = reader["Damage Doers"]
    >>> table.fields
    ['name', 'age', 'favorite_color']
    >>>
    >>> for row in table:
    ...     print(row.favorite_color)
    ...
    Red
    Red
    Red
    Red
    >>>
    >>> for row in table.matches_all(age="26"):
    ...     print(row.name)
    ...
    Mookie
    Xander
    >>>
    >>> for row in table.exclude_by(age="26"):
    ...     print(row.name)
    ...
    Andrew
    JD

Usage
-----

``class tableread.SimpleRSTReader(file_path)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Parse a reStructredText file, ``file_path``, and convert any simple tables into ``SimpleRSTTable`` objects.
    Individual tables can be accessed using the table name as the key (``SimpleRSTReader['table_name']``)

**data**
  An OrderedDict of the table(s) found in the reST file. The key is either the
  section header before the table name from the file, or ``Default`` for tables not under a header.
  For multiple tables in a section (or multiple ``Default`` tables),
  subsequent tables will have a incrementing number appended to the key: ``Default``, ``Default_2``, etc.
  The value is a ``SimpleRSTTable`` object.

**tables**
  A list of the table names; an alias for ``list(data.keys())``

**first**
  A helper to get the first table found in the file; an alias for
  ``list(self.data.values())[0]``


``class tableread.SimpleRSTTable(header, rows, column_spans)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    A representation of an individual table. In addition to the methods below,
    you may iterate over the table itself as a shortcut (``for entry in table:``),
    which will yield from ``table.data``.
    ``len(table)`` will also return the number of entries in ``table.data``.

**data**
  A list of namedtuples with ``fields`` as the names.

**fields**
  A tuple of the table fields, as used in the ``data`` namedtuple.
  Field names are adapted from table columns by lower-casing,
  and replacing spaces and periods with underscores.

**from_data(data)**
  A helper function to create an object with. Expects a prepared list of namedtuples.

**matches_all(**kwargs)**
  Given a set of key/value filters, returns a new TableRead object with only
  the filtered data, that can be iterated over.
  Values may be either a simple value (str, int) or a function that returns a boolean.
  See Quickstart_ for an example.

  Note: When filtering both keys and values are **not** case sensitive.

**exclude_by(**kwargs)**
  Given a set of key/value filters, returns a new TableRead object without the
  matching data, that can be iterated over.
  Values may be either a simple value (str, int) or a function that returns a boolean.
  See Quickstart_ for an example.

  Note: When filtering both keys and values are **not** case sensitive.

**get_fields(*fields)**
  Given a list of fields, return a list of only the values associated with those fields.
  A single field returns a list of values, multiple fields returns a list of value tuples.


.. _`simple tables`: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#simple-tables
