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
        "digit": int.from_bytes(file_header[0:2]),
        "version": int.from_bytes(file_header[2:4]),
        "unknown_1": int.from_bytes(file_header[4:8]),
        "db_size": int.from_bytes(file_header[8:12]),
        "zero": int.from_bytes(file_header[12:16]),
        "table_count": int.from_bytes(file_header[16:20]),
        "unknown_2": int.from_bytes(file_header[20:24]),
    }
    output = {"headers": headers, "tables": []}

    position = 0
    table_data = data[FILE_HEADER_SIZE:]
    for _ in range(headers["table_count"]):
        name = table_data[position : position + 4].decode()[::-1]
        offset = int.from_bytes(table_data[position + 4 : position + 8])

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
            "prior_crc": int.from_bytes(table_header[0:4]),
            "unknown_2": int.from_bytes(table_header[4:8]),
            "len_bytes": int.from_bytes(table_header[8:12]),
            "len_bits": int.from_bytes(table_header[12:16]),
            "zero": int.from_bytes(table_header[16:20]),
            "max_records": int.from_bytes(table_header[20:22]),
            "current_records": int.from_bytes(table_header[22:24]),
            "unknown_3": int.from_bytes(table_header[24:28]),
            "num_fields": table_header[28],
            "index_count": table_header[29],
            "zero_2": int.from_bytes(file_header[30:32]),
            "zero_3": int.from_bytes(table_header[32:36]),
            "header_crc": int.from_bytes(table_header[36:40]),
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
                "type": int.from_bytes(field_data[0:4]),
                "offset": int.from_bytes(field_data[4:8]),
                "name": field_data[8:12].decode()[::-1],
                "bits": int.from_bytes(field_data[12:16]),
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
