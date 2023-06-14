from typing import BinaryIO

import ncaadb.hex

FILE_HEADER_SIZE = 24
TABLE_HEADER_SIZE = 40
TABLE_DEFINITION_SIZE = 8
TABLE_FIELD_SIZE = 16


def read_db(db_file: BinaryIO) -> None:
    """Read an NCAA DB file into python-readable data.

    Args:
        db_file (BinaryIO): NCAA DB file
    """
    data = db_file.read()
    file_header = data[:FILE_HEADER_SIZE]

    headers = {
        "digit": ncaadb.hex.read_word(1, file_header),
        "version": ncaadb.hex.read_word(3, file_header),
        "unknown_1": ncaadb.hex.read_dword(7, file_header),
        "db_size": ncaadb.hex.read_dword(11, file_header),
        "zero": ncaadb.hex.read_dword(15, file_header),
        "table_count": ncaadb.hex.read_dword(19, file_header),
        "unknown_2": ncaadb.hex.read_dword(23, file_header),
    }
    output = {"headers": headers, "tables": []}

    position = 0
    table_data = data[FILE_HEADER_SIZE:]
    for _ in range(headers["table_count"]):
        name = ncaadb.hex.read_text(position + 3, 4, table_data)
        offset = ncaadb.hex.read_dword(position + 7, table_data)

        definition = {"name": name, "offset": offset}
        table = {"definition": definition}
        output["tables"].append(table)

        position += TABLE_DEFINITION_SIZE
