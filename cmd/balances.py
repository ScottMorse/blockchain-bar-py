
from database.state import State

def describe_balances():
    state = State.init_from_disk()
    print(f"Account balances at {state.snapshot[:8]}... : \n_________________")
    for account, balance in state.balances.items():
        print(f"{account}: {balance:,}")