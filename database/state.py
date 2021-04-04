from io import TextIOWrapper
import json
import io
import pathlib
import os
from time import time
from hashlib import sha256
from copy import deepcopy
from typing import Dict, List

from .genesis import load_genesis
from .tx import Tx
from .block import Block, BlockHeader

mod_dir = pathlib.Path(__file__).parent.absolute()

genesis_path = os.path.join(mod_dir, 'genesis.json')
legacy_db_path = os.path.join(mod_dir, 'tx.db')
db_path = os.path.join(mod_dir, 'block.db')

class State:

    def __init__(self, *, balances: Dict[str, int], tx_mempool: List[Tx]):
        self._balances = balances
        self._tx_mempool = tx_mempool
        self._latest_block_hash = "0" * 32

    @property
    def balances(self) -> Dict[str, int]:
        return self._balances

    @property
    def tx_mempool(self) -> List[Tx]:
        return self._tx_mempool

    @property
    def latest_block_hash(self) -> str:
        return self._latest_block_hash

    @classmethod
    def init_from_disk_legacy(cls):

        gen = load_genesis(os.path.join(pathlib.Path(__file__).parent.absolute(), 'genesis.json'))

        state = cls(balances=deepcopy(gen.balances), tx_mempool=[])
        with open(legacy_db_path) as f:
            for line in f.readlines():
                if line != '\n':
                    state.add(Tx.init_from_json(json.loads(line)))
    
        return state

    @classmethod
    def init_from_disk(cls):

        gen = load_genesis(os.path.join(pathlib.Path(__file__).parent.absolute(), 'genesis.json'))

        state = cls(balances=deepcopy(gen.balances), tx_mempool=[])
        with open(db_path) as f:
            for line in f.readlines():
                if line != '\n':
                    state.add_block(Block.init_from_json(json.loads(line)))
    
        return state

    class InsufficientBalanceError(Exception):
        pass

    def add_block(self, block: Block):
        [self.add(tx) for tx in block.txs]

    def add(self, tx: Tx):
        self.apply(tx)
        self.tx_mempool.append(tx)

    def persist(self):
        if len(self.tx_mempool) == 0:
            print(f"No TXs to persist")
            return

        block = Block(
            header=BlockHeader(
                parent_hash=self.latest_block_hash, 
                time=time()
            ),
            txs=self.tx_mempool
        )

        block_json = block.to_json()
        print(f"Persisting block: {json.dumps(block_json, indent=2)}")
        with open(db_path, 'a') as f:
            f.write(f"{json.dumps(block_json, separators=[',',':'])}\n")

        self._latest_block_hash = block.create_hash()
        self._tx_mempool = []

        return self.latest_block_hash

    def apply_block(self, block: Block):
        [self.apply(tx) for tx in block.txs]

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