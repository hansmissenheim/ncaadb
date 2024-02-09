"""The functions used for reading ncaa db files.

The core function of this module, `read_db()`, is the main method for allowing users to
open an ncaa db file. The function takes an opened `BinaryIO` stream and returns a
`File` class object containing file header information and the db's total tabular
data.

Usage example:

    with open(filename, "wb") as ncaa_db_file:
        file = ncaadb.read_file(ncaa_db_file)

    players_table = file["PLAY"]
"""

import struct
from typing import BinaryIO

import pandas as pd

import ncaadb.hex
from ncaadb.const import (
    FILE_HEADER_SIZE,
    TABLE_DEFINITION_SIZE,
    TABLE_FIELD_SIZE,
    TABLE_HEADER_SIZE,
)
from ncaadb.file import Field, FieldType, File, FileHeader, Table, TableHeader


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