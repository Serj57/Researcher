from .config import DATABASE
from .config import TABLE

from .methods import IMethod
from .methods import PositionalMethod
from .methods import PacketPositionalMethod

from .parser import TsharkParser

import sqlite3

__all__ = [
    "Analyzer",
    "PositionalMethod",
    "PacketPositionalMethod",
    "TsharkParser"
]

_create_table = f"""
    CREATE TABLE IF NOT EXISTS {TABLE} (
        stream INTEGER NOT NULL,
        packet INTEGER NOT NULL,
        data   TEXT);
"""
db = sqlite3.connect(DATABASE)
db.execute(_create_table)


class Analyzer:
    def __init__(self) -> None:
        self._method = None
    
    def set_method(self, method:IMethod):
        self._method = method

    def start(self):
        if not self._method:
            raise Exception
        return self._method.run()