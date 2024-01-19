def read_string(data: bytes, bits: int, offset: int) -> str:
    start_byte = offset // 8
    end_byte = (offset + bits) // 8
    return data[start_byte:end_byte].decode("latin-1").replace("\00", "")


def read_bytes(data: bytes, bits: int, offset: int) -> str:
    start_byte = offset // 8
    end_byte = (offset + bits) // 8
    return data[start_byte:end_byte].hex()


def read_nums(data: bytes, bits: int, offset: int) -> int:
    byte_offset = offset // 8
    bit_offset = offset % 8
    value = 0
    for i in range(bits):
        value <<= 1
        value |= (data[byte_offset] >> (7 - bit_offset)) & 1
        bit_offset += 1
        if bit_offset >= 8:
            byte_offset += 1
            bit_offset = 0
    return value
