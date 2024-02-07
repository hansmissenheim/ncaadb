from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

import ncaadb

if TYPE_CHECKING:
    import pandas as pd


def _hash_tables(df: pd.DataFrame) -> str:
    df_str = df.to_string(index=False)
    sha256_hash = hashlib.sha256()
    sha256_hash.update(df_str.encode("utf-8"))
    return sha256_hash.hexdigest()


@pytest.mark.parametrize(
    ("usr_data_file", "hashed_json_file"),
    [
        ("pre.USR-DATA", "pre.json"),
        ("post.USR-DATA", "post.json"),
        ("load.USR-DATA", "load.json"),
    ],
)
def test_read_db(usr_data_file: str, hashed_json_file: str) -> None:
    with Path(f"tests/test_reader/{hashed_json_file}").open("r") as file:
        hashed_json = json.load(file)

    with Path(f"tests/test_reader/{usr_data_file}").open("rb") as file:
        db_file = ncaadb.read_db(file)

    hashed_data = {
        table.name: _hash_tables(table.data) for table in db_file.table_dict.values()
    }

    for data_hash, json_hash in zip(hashed_data.values(), hashed_json.values()):
        assert data_hash == json_hash
