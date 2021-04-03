from io import TextIOWrapper
import json
import io
import pathlib
import os
from hashlib import sha256
from copy import deepcopy
from typing import Dict, List

from .genesis import load_genesis
from .tx import Tx

mod_dir = pathlib.Path(__file__).parent.absolute()

genesis_path = os.path.join(mod_dir, 'genesis.json')
db_path = os.path.join(mod_dir, 'tx.db')

class State:

    def __init__(self, *, balances: Dict[str, int], tx_mempool: List[Tx]):
        self._balances = balances
        self._tx_mempool = tx_mempool
        self.save_snapshot()

    @property
    def balances(self) -> Dict[str, int]:
        return self._balances

    @property
    def tx_mempool(self) -> List[Tx]:
        return self._tx_mempool

    @property
    def snapshot(self):
        return self._snapshot

    @classmethod
    def init_from_disk(cls):

        gen = load_genesis(os.path.join(pathlib.Path(__file__).parent.absolute(), 'genesis.json'))

        state = cls(balances=deepcopy(gen.balances), tx_mempool=[])
        with open(db_path) as f:
            for line in f.readlines():
                if line != '\n':
                    state.apply(Tx.init_from_json(json.loads(line)))

        return state

    class InsufficientBalanceError(Exception):
        pass

    def add(self, tx: Tx):
        self.apply(tx)
        self.tx_mempool.append(tx)

    def persist(self):
        with open(db_path, 'a') as f:
            for tx in deepcopy(self.tx_mempool):
                print(f'TX to be persisted: {tx.to_json()}.')
                f.write(f"\n{json.dumps(tx.to_json(), separators=[',', ':'])}")
                self._tx_mempool = self._tx_mempool[1:]
                print('TX successfully persisted.')
        self.save_snapshot()
        print(f'New DB Snapshot: {self.snapshot}')

    def apply(self, tx: Tx):
        if not self.balances.get(tx.to_acc):
            self.balances[tx.to_acc] = 0

        if tx.from_acc and not self.balances.get(tx.from_acc):
            self.balances[tx.from_acc] = 0

        if tx.is_reward:
            self.balances[tx.to_acc] += tx.value
            return

        if self.balances[tx.from_acc] < tx.value:
            raise self.InsufficientBalanceError(f"Insufficient balance for transfer of {tx.value} from {tx.from_acc} to {tx.to_acc}")

        self.balances[tx.from_acc] -= tx.value
        self.balances[tx.to_acc] += tx.value

    def save_snapshot(self):
        hashed = sha256()
        with open(db_path, 'rb') as f:
            while True:
                data = f.read(64000)
                if not data:
                    break
                hashed.update(data)
        self._snapshot = hashed.hexdigest()