import dataclasses
import math
import struct
from dataclasses import dataclass
from typing import Any, BinaryIO

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

    def __post_init__(self):
        if isinstance(self.name, bytes):
            self.name = self.name.decode()[::-1]


@dataclass
class Table:
    name: str
    offset: int
    header: TableHeader | None = None
    fields: list[Field] = dataclasses.field(default_factory=list)


def read_db(db_file: BinaryIO) -> dict[str, Any]:
    """Read an NCAA DB file into python-readable data.

    Args:
        db_file (BinaryIO): NCAA DB file

    Returns:
        dict[str, Any]: Dictionary containing file headers and table data
    """
    buffer = db_file.read(FILE_HEADER_SIZE)
    header = FileHeader(*struct.unpack(">HHIIIII", buffer))

    tables = {}
    for _ in range(header.table_count):
        buffer = db_file.read(TABLE_DEFINITION_SIZE)
        name, offset = struct.unpack(">4sI", buffer)
        name = name.decode()[::-1]
        tables[name] = Table(name, offset)

    header_start_byte = db_file.tell()
    for name, table in tables.items():
        bytes_to_skip = (header_start_byte + table.offset) - db_file.tell()
        db_file.read(bytes_to_skip)

        buffer = db_file.read(TABLE_HEADER_SIZE)
        table.header = TableHeader(*struct.unpack(">IIIIIHHIBBHII", buffer))

        for _ in range(table.header.num_fields):
            buffer = db_file.read(TABLE_FIELD_SIZE)
            field = Field(*struct.unpack(">II4sI", buffer))
            table.fields.append(field)
