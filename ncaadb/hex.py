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
