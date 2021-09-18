import json
import pathlib
from time import time
from copy import deepcopy
from typing import Dict, List, Union

from .genesis import Genesis
from .tx import Tx
from .block import Block, BlockHeader
from .fs import get_blocks_db_file_path, get_genesis_file_path, init_data_dir
from .config import BLOCK_SIZE

mod_dir = pathlib.Path(__file__).parent.absolute()

class State:

    def __init__(self, *, balances: Dict[str, int], tx_mempool: List[Tx]):
        self._balances = balances
        self._tx_mempool = tx_mempool
        self._latest_block_hash = "0" * 32
        self._latest_block = None

    @property
    def balances(self) -> Dict[str, int]:
        return self._balances

    @property
    def tx_mempool(self) -> List[Tx]:
        return self._tx_mempool

    @property
    def latest_block_hash(self) -> str:
        return self._latest_block_hash

    @property
    def latest_block(self) -> Union[Block, None]:
        return self._latest_block

    @classmethod
    def init_from_disk(cls, data_dir: str):
        init_data_dir(data_dir)

        gen = Genesis.load_from_disk(get_genesis_file_path(data_dir))

        state = cls(balances=deepcopy(gen.balances), tx_mempool=[])
        with open(get_blocks_db_file_path(data_dir)) as f:
            lines = f.readlines()
            for i in range(len(lines)):
                line = lines[i]
                if line != '\n':
                    block = Block.init_from_json(json.loads(line)['block'])
                    state.apply_block(block)
                    if i == len(lines) - 1:
                        state._latest_block = block
                        state._latest_block_hash = block.create_hash()
    
        return state

    class InsufficientBalanceError(Exception):
        pass

    def add_block(self, block: Block):
        [self.add(tx) for tx in block.txs]

    def add(self, tx: Tx):
        self.apply(tx)
        self.tx_mempool.append(tx)

    def persist(self, data_dir: str):
        if len(self.tx_mempool) == 0:
            print(f"No TXs to persist")
            return

        block = Block(
            header=BlockHeader(
                parent=self.latest_block_hash, 
                time=time()
            ),
            txs=self.tx_mempool
        )

        block_json = block.to_json()
        print(f"Persisting block: {json.dumps(block_json, indent=2)}")
        with open(get_blocks_db_file_path(data_dir), 'a') as f:
            f.write(f"{json.dumps(block_json, separators=[',',':'])}\n")

        self._latest_block_hash = block.create_hash()
        self._latest_block = block
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