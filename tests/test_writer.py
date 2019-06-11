import pytest
import shutil
import tempfile

import attr

import tableread
from tableread import writer


@pytest.fixture
def temp_dir():
    """Creates and return a tmpdir for testing"""
    log_dir = tempfile.mkdtemp()
    yield log_dir
    shutil.rmtree(log_dir)


@pytest.fixture
def table_one_data():
    return [
        {"City": "Austin", "Description": "Weird"},
        {"City": "Houston", "Description": "Chain Restaurants"},
        {"City": "Lubbock", "Description": "Flat"},
    ]


@pytest.fixture
def table_two_data():
    return [
        {"City": "Miami", "Description": "Not Texas"},
        {"City": "Los Angeles", "Description": "Not Texas"},
        {"City": "Seattle", "Description": "Not Texas"},
    ]


def test_write_table(temp_dir, table_one_data, table_two_data):
    w = writer.SimpleRSTWriter(
        temp_dir + "test_file.rst",
        ("Cool Cities", table_one_data),
        ("Not Texas Cities", table_two_data),
    )
    w.write_tables()


def _convert_col_names(d):
    return {k.lower().replace(" ", "_"): v for k, v in d.items()}


def test_table_data(temp_dir, table_one_data):
    path = temp_dir + "test_file.rst"
    writer.SimpleRSTWriter(path, ("Cool Cities", table_one_data)).write_tables()
    table = tableread.SimpleRSTReader(path).first
    assert all(
        attr.asdict(table_row) == _convert_col_names(test_row)
        for table_row, test_row in zip(table, table_one_data)
    )
