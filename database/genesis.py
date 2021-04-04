import json
from typing import Dict

class Genesis:

    JSON = {
        "genesis_time": "2019-03-18T00:00:00.000000000Z",
        "chain_id": "the-blockchain-bar-ledger",
        "balances": {
            "andrej": 1000000
        }
    }

    @classmethod
    def load_from_disk(cls, path: str):
        with open(path) as f:
            return cls(balances=json.load(f)['balances'])

    @classmethod
    def write_to_disk(cls, path: str):
        with open(path, 'w') as f:
            f.write(json.dumps(cls.JSON, indent=2))

    # balances: map of account ID to balance amount
    def __init__(self, *, balances: Dict[str, int]):
        self._balances = balances

    @property
    def balances(self) -> Dict[str, int]:
        return self._balances