"""The core classes and functions used for reading Ncaa DB Files.

The classes within this module includes `File` representing the Ncaa Db File, along with
classes for each part comprising the file. This `File` class is what is returned when
reading an Ncaa DB File with the `read_db()` function. This function is used to read an
Ncaa DB File from an opened `BinaryIO` stream, and return each database table as a
`pandas.Dataframe`, which can then be modified as neccessary.

Usage example:

    with open(filename, "wb") as ncaa_db_file:
        file = ncaadb.read_file(ncaa_db_file)

    players_table = file["PLAY"]
"""

import dataclasses
import struct
from dataclasses import dataclass
from enum import IntEnum
from typing import BinaryIO

import pandas as pd

import ncaadb.hex

FILE_HEADER_SIZE = 24
TABLE_HEADER_SIZE = 40
TABLE_DEFINITION_SIZE = 8
TABLE_FIELD_SIZE = 16


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
class Field:
    type: int
    offset: int
    name: bytes | str
    bits: int

    def __post_init__(self) -> None:
        if isinstance(self.name, bytes):
            self.name = self.name.decode()[::-1]
        self.type = FieldType(self.type)


class FieldType(IntEnum):
    STRING = 0
    BINARY = 1
    SINT = 2
    UINT = 3
    FLOAT = 4


@dataclass
class Table:
    name: str
    offset: int
    header: TableHeader | None = None
    fields: list[Field] = dataclasses.field(default_factory=list)
    data: pd.DataFrame | None = None


@dataclass
class File:
    header: FileHeader
    table_dict: dict[str, Table]

    def __getitem__(self, table_name: str) -> pd.DataFrame | None:
        return self.table_dict[table_name].data

    def __setitem__(self, table_name: str, table_data: pd.DataFrame) -> None:
        self.table_dict[table_name].data = table_data


def read_file_header(db_file: BinaryIO) -> FileHeader:
    buffer = db_file.read(FILE_HEADER_SIZE)
    return FileHeader(*struct.unpack(">HHIIIII", buffer))


def read_table_definitions(db_file: BinaryIO, table_count: int) -> dict[str, Table]:
    tables = {}
    for _ in range(table_count):
        buffer = db_file.read(TABLE_DEFINITION_SIZE)
        name, offset = struct.unpack(">4sI", buffer)
        name = name.decode()[::-1]
        tables[name] = Table(name, offset)
    return tables


def read_table_fields(db_file: BinaryIO, table: Table) -> None:
    for _ in range(table.header.num_fields):
        buffer = db_file.read(TABLE_FIELD_SIZE)
        field = Field(*struct.unpack(">II4sI", buffer))
        match field.type:
            case FieldType.STRING:
                field.read_func = ncaadb.hex.read_string
            case FieldType.BINARY:
                field.read_func = ncaadb.hex.read_bytes
            case _:
                field.read_func = ncaadb.hex.read_nums
        table.fields.append(field)


def read_table_records(db_file: BinaryIO, table: Table) -> None:
    records = []
    for _ in range(table.header.current_records):
        buffer = db_file.read(table.header.len_bytes)
        records.append(buffer)

    data = []
    columns = [field.name for field in table.fields]
    for buffer in records:
        record = []
        for field in table.fields:
            record.append(field.read_func(buffer, field.bits, field.offset))
        data.append(record)
    table.data = pd.DataFrame(data, columns=columns)


def read_table_data(db_file: BinaryIO, tables: dict[str, Table]) -> None:
    header_start_byte = db_file.tell()
    for table in tables.values():
        bytes_to_skip = (header_start_byte + table.offset) - db_file.tell()
        db_file.read(bytes_to_skip)

        buffer = db_file.read(TABLE_HEADER_SIZE)
        table.header = TableHeader(*struct.unpack(">IIIIIHHIBBHII", buffer))
        read_table_fields(db_file, table)
        read_table_records(db_file, table)


def read_db(db_file: BinaryIO) -> File:
    """Read an NCAA DB file into python-readable data.

    Args:
        db_file (BinaryIO): Open file stream to NCAA DB file

    Returns:
        File: NCAA DB File object containing header info and table data
    """
    file_header = read_file_header(db_file)
    table_dict = read_table_definitions(db_file, file_header.table_count)
    file = File(file_header, table_dict)

    read_table_data(db_file, file.table_dict)
    return file
