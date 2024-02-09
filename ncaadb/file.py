"""The classes comprising the Ncaa DB File representation as `File`."""

from dataclasses import dataclass, field
from enum import IntEnum

import pandas as pd


class FieldType(IntEnum):
    STRING = 0
    BINARY = 1
    SINT = 2
    UINT = 3
    FLOAT = 4


@dataclass
class Field:
    type: int
    offset: int
    name: bytes | str
    bits: int

    def __post_init__(self) -> None:
        if isinstance(self.name, bytes):
            self.name = self.name.decode()[::-1]
        self.type = FieldType(self.type)


@dataclass
class TableHeader:
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
    name: str
    offset: int
    header: TableHeader | None = None
    fields: list[Field] = field(default_factory=list)
    data: pd.DataFrame | None = None


@dataclass
class FileHeader:
    digit: int
    version: int
    unknown_1: int
    db_size: int
    zero: int
    table_count: int
    unknown_2: int


@dataclass
class File:
    header: FileHeader
    table_dict: dict[str, Table]

    def __getitem__(self, table_name: str) -> pd.DataFrame | None:
        return self.table_dict[table_name].data

    def __setitem__(self, table_name: str, table_data: pd.DataFrame) -> None:
        self.table_dict[table_name].data = table_data
