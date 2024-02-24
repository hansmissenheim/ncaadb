# ncaadb

Ncaadb is a Python package created for the handling of DB save files from EA Sports NCAA games.

## Installation

Ncaadb is published to PyPI and is available using `pip` or any other Python package manager.

    pip install ncaadb


## Usage

The data from a DB file is loaded into a `File` by opening a file stream and sending it into the `read_db` function.

``` python
import ncaadb

with open("saves/USR-DATA", "rb") as f:
    db_data = ncaadb.read_db(f)
```

The contents of a table can then be accessed using the indexer operator, `[]`, and the table's name as the index. This will return the tabular data as a `pandas.DataFrame`. The tabular data can be set using the same method. 

``` python
player_data = db_data["PLAY"]
modified_player_data = player_data.replace(0, 1)
db_data["PLAY"] = modified_player_data
```
