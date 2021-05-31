import json
from typing import List
from hashlib import sha256

from .tx import Tx

class BlockHeader:

    @classmethod
    def init_from_json(cls, j: dict):
        return cls(
            parent=j["parent"],
            number=j["number"],
            time=j["time"]
        )

    def __init__(self, *, parent: str, number: int, time: float):
        self._parent = parent
        self._number = number
        self._time = time

    @property
    def parent(self) -> str:
        return self._parent

    @property
    def number(self) -> int:
        return self._number

    @property
    def time(self) -> float:
        return self._time

    def to_json(self) -> dict:
        return {
            "parent": self.parent,
            "number": self.number,
            "time": self.time
        }

class Block:

    @classmethod
    def init_from_json(cls, j: dict):
        return cls(
            header=BlockHeader.init_from_json(j["header"]),
            txs=[Tx.init_from_json(t) for t in j["txs"]]
        )

    def __init__(self, *, header: BlockHeader, txs: List[Tx]):
        self._header = header
        self._txs = txs

    @property
    def header(self) -> BlockHeader:
        return self._header

    @property
    def txs(self) -> List[Tx]:
        return self._txs

    def to_json(self) -> dict:
        return {
            "header": self.header.to_json(),
            "txs": [tx.to_json() for tx in self.txs]
        }

    def create_hash(self) -> str:
        return sha256(str.encode(json.dumps(self.to_json()))).hexdigest()