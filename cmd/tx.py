 
from database.tx import Tx
from database.state import State

def add_tx(*, to_acc: str, from_acc: str, is_reward: bool, data: str, amount: int):
    if not to_acc:
        raise ValueError(f"No 'to' account specified")
    if not is_reward and not from_acc:
        raise ValueError(f"No 'from' account specified")

    tx = Tx(
        from_acc=to_acc if is_reward else from_acc,
        to_acc=to_acc,
        value=amount,
        data="reward" if is_reward else data
    )

    state = State.init_from_disk()
    state.add(tx)

    print(f"Awarded {amount} to {to_acc}" if is_reward else f"Transfer {amount} from {from_acc} to {to_acc}")
    print("Transaction successfully added.")

    state.persist()