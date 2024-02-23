"""The classes comprising the Ncaa DB File representation as `File`."""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum

import pandas as pd

import ncaadb.hex


class FieldType(IntEnum):
    """Enum for the different data types of fields in the Ncaa DB File."""

    STRING = 0
    BINARY = 1
    SINT = 2
    UINT = 3
    FLOAT = 4


@dataclass
class Field:
    """Class to represent the tables' fields in the Ncaa DB File."""

    type: int
    offset: int
    name: bytes | str
    bits: int
    read_func: Callable[[bytes, int, int], int | str] | None = None

    def __post_init__(self) -> None:
        """Post init method to decode the name and convert the type to FieldType."""
        if isinstance(self.name, bytes):
            self.name = self.name.decode()[::-1]

        self.type = FieldType(self.type)
        match self.type:
            case FieldType.STRING:
                self.read_func = ncaadb.hex.read_string
            case FieldType.BINARY:
                self.read_func = ncaadb.hex.read_bytes
            case _:
                self.read_func = ncaadb.hex.read_nums


@dataclass
class TableHeader:
    """Class to store the tables' headers info from the Ncaa DB File."""

    prior_crc: int
    unknown_2: int
    len_bytes: int
    len_bits: int
    zero: int
    max_records: int
    current_records: int
    unknown_3: int
    num_fields: int
    index_count: int
    zero_2: int
    zero_3: int
    header_crc: int


@dataclass
class Table:
    """Class to represent the tables in the Ncaa DB File."""

    name: str
    offset: int
    header: TableHeader | None = None
    fields: list[Field] = field(default_factory=list)
    data: pd.DataFrame | None = None


@dataclass
class FileHeader:
    """Class to store the file header info from the Ncaa DB File."""

    digit: int
    version: int
    unknown_1: int
    db_size: int
    zero: int
    table_count: int
    unknown_2: int


@dataclass
class File:
    """Class to represent the Ncaa DB File."""

    header: FileHeader
    table_dict: dict[str, Table]

    def __getitem__(self, table_name: str) -> pd.DataFrame | None:
        """Get the table data from the table name."""
        return self.table_dict[table_name].data

    def __setitem__(self, table_name: str, table_data: pd.DataFrame) -> None:
        """Set the table data for the table name.

        Args:
            table_name (str): The name of the table to set the data for
            table_data (pd.DataFrame): The data to set for the table
        """
        self.table_dict[table_name].data = table_data
