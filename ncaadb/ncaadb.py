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
class Table:
    name: str
    offset: int


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
