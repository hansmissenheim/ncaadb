def read_text(index: int, length: int, data: bytes) -> str:
    if length > len(data):
        raise ValueError(
            "length must not be greater than the passed in data array length."
        )
    elif index >= len(data):
        raise ValueError(
            "index must not be greater than the passed in data array length."
        )

    text = ""
    for i in range(length):
        text += chr(data[index - i])
    return text


def read_word(index: int, data: bytes) -> int:
    if index < 1:
        raise ValueError("index must be equal to or greater than 1.")
    elif index >= len(data):
        raise ValueError(
            "index must not be greater than the passed in data array length."
        )

    return data[index] | data[index - 1] << 8


def read_dword(index: int, data: bytes) -> int:
    if index < 3:
        raise ValueError("index must be equal to or greater than 3.")
    elif index >= len(data):
        raise ValueError(
            "index must not be greater than the passed in data array length."
        )

    return (
        data[index]
        | data[index - 1] << 8
        | data[index - 2] << 16
        | data[index - 3] << 24
    )


def read_string(record_data: bytes, field: dict[str, int | str]):
    string = ""
    for i in range(field.get("bits") // 8):
        b = record_data[(field.get("offset") // 8) + i]
        if b != 0:
            string += chr(b)
    return string


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
