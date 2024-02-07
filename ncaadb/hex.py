"""Functions used to read hex values from hex records.

The tabular data found in Ncaa DB Files is saved for each row in an uninterrupted block
of hex data. Where the data is split for each column and the output data type is found
in the `Field` data. This data along with the block of data is used to read a given row
and column's record.
"""


def read_string(data: bytes, bits: int, offset: int) -> str:
    """Reads tabular record data into a string.

    The strings saved in the hex record data uses blank bits that must be replaced with
    empty strings when decoded in order to maintain proper representation.

    Args:
        data (bytes): A tabular data row's hex record data
        bits (int): The field's data length in bits
        offset (int): The field's data offset to the start in record data

    Returns:
        str: String representation of the row's field-specefic record
    """
    start_byte = offset // 8
    end_byte = (offset + bits) // 8
    return data[start_byte:end_byte].decode("latin-1").replace("\00", "")


def read_bytes(data: bytes, bits: int, offset: int) -> str:
    """Reads tabular record data into a string represenation of hex bytes.

    Args:
        data (bytes): A tabular data row's hex record data
        bits (int): The field's data length in bits
        offset (int): The field's data offset to the start in record data

    Returns:
        str: _description_
    """
    start_byte = offset // 8
    end_byte = (offset + bits) // 8
    return data[start_byte:end_byte].hex()


def read_nums(data: bytes, bits: int, offset: int) -> int:
    """Reads tabular record data into an integer.

    Args:
        data (bytes): A tabular data row's hex record data
        bits (int): The field's data length in bits
        offset (int): The field's data offset to the start in record data

    Returns:
        int: Integer representation of the row's field-specefic record
    """
    byte_offset = offset // 8
    bit_offset = offset % 8
    value = 0
    for _ in range(bits):
        value <<= 1
        value |= (data[byte_offset] >> (7 - bit_offset)) & 1
        bit_offset += 1
        if bit_offset >= 8:
            byte_offset += 1
            bit_offset = 0
    return value
