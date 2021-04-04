
from database.state import State

def describe_balances(*, data_dir: str):
    state = State.init_from_disk(data_dir)
    print(f"Account balances: \n_________________")
    for account, balance in state.balances.items():
        print(f"{account}: {balance:,}")