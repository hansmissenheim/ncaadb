from typing import BinaryIO


def read_db(db_file: BinaryIO) -> None:
    """Read an NCAA DB file into python-readable data.

    Args:
        db_file (BinaryIO): NCAA DB file
    """
    data = db_file.read()
