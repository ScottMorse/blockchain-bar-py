import atexit
from flask import Flask, request, Response

from database.config import BLOCK_SIZE
from database.state import State
from database.tx import Tx

app = Flask('app')

DATA_DIR = '_db'

state = State.init_from_disk(DATA_DIR)

atexit.register(lambda: state.persist(DATA_DIR))

@app.route('/')
def home():
    return { 'status': 'UP' }

@app.route('/balances/list', methods=['GET'])
def balances():
    return state.balances

@app.route('/tx/add', methods=['POST'])
def add_tx():
    req = request.get_json()

    to_acc = req.get('to')
    from_acc = req.get('from')
    is_reward = req.get('is_reward')
    amount = req.get('amount')
    data = req.get('data')

    err = None

    if not to_acc:
        err = f"No 'to' account specified"
    if not is_reward and not from_acc:
        err = f"No 'from' account specified"

    if err:
        return Response({ 'error': err }, status=400)

    tx = Tx(
        from_acc=to_acc if is_reward else from_acc,
        to_acc=to_acc,
        value=amount,
        data="reward" if is_reward else data
    )

    state.add(tx)

    if len(state.tx_mempool) >= BLOCK_SIZE:
        state.persist(DATA_DIR)

    return { "message": "Transaction successfully added", "details": f"Awarded {amount} to {to_acc}" if is_reward else f"Transfer {amount} from {from_acc} to {to_acc}" }