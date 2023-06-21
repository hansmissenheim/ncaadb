def read_string(data: bytes, bits: int, offset: int) -> str:
    start_byte = offset // 8
    end_byte = (offset + bits) // 8
    return data[start_byte:end_byte].decode("latin-1").replace("\00", "")


def read_bytes(record_data: bytes, field: dict[str, int | str]):
    bites = []
    for i in range(field.get("bits") // 8):
        bites.insert(i, record_data[(field.get("offset") // 8) + i])
    return bites


def read_bits(record_data: bytes, offset: int, bits_to_read: int):
    ret = 0
    mask = 1
    for i in range(bits_to_read, 0, -1):
        if record_data[i + (offset - 1)]:
            ret = ret | mask
        mask = mask << 1
    return ret


def bit_array(byte: int):
    return [int(digit) for digit in f"{byte:08b}"]
