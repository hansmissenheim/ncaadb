import math
from typing import Any, BinaryIO

import ncaadb.hex

FILE_HEADER_SIZE = 24
TABLE_HEADER_SIZE = 40
TABLE_DEFINITION_SIZE = 8
TABLE_FIELD_SIZE = 16


def read_db(db_file: BinaryIO) -> dict[str, Any]:
    """Read an NCAA DB file into python-readable data.

    Args:
        db_file (BinaryIO): NCAA DB file

    Returns:
        dict[str, Any]: Dictionary containing file headers and table data
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

    header_start = position
    output["headers"]["data_start"] = header_start + FILE_HEADER_SIZE
    for table in output["tables"]:
        position = header_start + table["definition"]["offset"]
        end = position + TABLE_HEADER_SIZE
        table_header = table_data[position:end]

        header = {
            "prior_crc": ncaadb.hex.read_dword(3, table_header),
            "unknown_2": ncaadb.hex.read_dword(7, table_header),
            "len_bytes": ncaadb.hex.read_dword(11, table_header),
            "len_bits": ncaadb.hex.read_dword(15, table_header),
            "zero": ncaadb.hex.read_dword(19, table_header),
            "max_records": ncaadb.hex.read_word(21, table_header),
            "current_records": ncaadb.hex.read_word(23, table_header),
            "unknown_3": ncaadb.hex.read_dword(27, table_header),
            "num_fields": table_header[28],
            "index_count": table_header[29],
            "zero_2": ncaadb.hex.read_word(31, table_header),
            "zero_3": ncaadb.hex.read_dword(35, table_header),
            "header_crc": ncaadb.hex.read_dword(39, table_header),
            "field_start": end,
            "data_start": end + table_header[28] * TABLE_FIELD_SIZE,
        }

        table["header"] = header

    for table in output["tables"]:
        table["fields"] = []
        position = table["header"]["field_start"]
        end = position + TABLE_FIELD_SIZE

        for _ in range(table["header"]["num_fields"]):
            field_data = table_data[position : position + TABLE_FIELD_SIZE]

            field = {
                "type": ncaadb.hex.read_dword(3, field_data),
                "offset": ncaadb.hex.read_dword(7, field_data),
                "name": ncaadb.hex.read_text(11, 4, field_data),
                "bits": ncaadb.hex.read_dword(15, field_data),
                "records": [],
            }

            table["fields"].append(field)
            position += TABLE_FIELD_SIZE

    for table in output["tables"]:
        data_start = table["header"]["data_start"]
        len_bytes = table["header"]["len_bytes"]
        records = table["header"]["current_records"]

        for field in table["fields"]:
            for i in range(records):
                position = data_start + i * len_bytes
                end = position + len_bytes
                record_data = table_data[position:end]

                value = None
                match field["type"]:
                    case 0:
                        value = ncaadb.hex.read_string(record_data, field)
                    case 1:
                        value = ncaadb.hex.read_bytes(record_data, field)
                    case 2 | 3 | 4:
                        arr = [
                            *record_data[
                                math.floor(field["offset"] / 8) : math.ceil(
                                    (field["bits"] + field["offset"]) / 8
                                )
                            ]
                        ]
                        bit_list = [ncaadb.hex.bit_array(byte) for byte in arr]
                        all_bits = [item for sublist in bit_list for item in sublist]
                        value = ncaadb.hex.read_bits(
                            all_bits, field["offset"] % 8, field["bits"]
                        )

                field["records"].append({"value": value, "record_number": i})
    return output
