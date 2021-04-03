import json
from typing import Dict

class Genesis:

    # balances: map of account ID to balance amount
    def __init__(self, *, balances: Dict[str, int]):
        self._balances = balances

    @property
    def balances(self) -> Dict[str, int]:
        return self._balances

def load_genesis(path: str) -> Genesis:
    with open(path) as f:
        return Genesis(balances=json.load(f)['balances'])
