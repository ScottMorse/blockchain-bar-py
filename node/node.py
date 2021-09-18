import atexit
import requests
from time import sleep
from flask.app import Flask, request, Response
from typing import Dict, Union

from database.state import State
from database.tx import Tx
from database.config import BLOCK_SIZE

from .peer_node import PeerNode

SYNC_WAIT_SEC = 30

class Node:

    def __init__(self, *, data_dir: str, port: int, bootstrap_node: PeerNode, is_bootstrap = False):
        self._data_dir = data_dir
        self._port = port
        self._known_peers = { bootstrap_node.url: bootstrap_node } if bootstrap_node else {}
        self._state = State.init_from_disk(data_dir=data_dir)
        self._is_bootstrap = is_bootstrap

    @property
    def data_dir(self) -> str:
        return self._data_dir
    
    @property
    def port(self) -> int:
        return self._port

    @property
    def known_peers(self) -> Dict[str, PeerNode]:
        return self._known_peers

    @property
    def is_bootstrap(self) -> bool:
        return self._is_bootstrap

    @property
    def state(self) -> Union[State, None]:
        return self._state

    def sync(self):
        if self.is_bootstrap:
            return

        new_blocks_count = 0
        for peer in self.known_peers.values():
            status = requests.get(f"http://{peer.ip}:{peer.port}/node/status").json()

            if status['number'] > self.state.latest_block.header.number:
                new_blocks_count = status['number'] - self.state.latest_block.header.number

            for url, peer in status.get('peers_known'):
                if not self.known_peers.get(url):
                    peer_node = PeerNode.from_json(peer)
                    self.known_peers[url] = peer_node

    def run(self):

        app = Flask('node')

        atexit.register(lambda: self.state.persist(self.data_dir))

        @app.route('/')
        def home():
            return "UP"

        @app.route('/node/status')
        def node_status():
            if self.state.latest_block:
                return { 
                    'hash': self.state.latest_block_hash, 
                    'number': self.state.latest_block.header.number,
                    'peers_known': { peer.url: peer.to_json() for url, peer in self.known_peers.items() }
                }
            return { 'hash': None, 'number': None }

        @app.route('/balances/list', methods=['GET'])
        def balances():
            return self.state.balances

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

            self.state.add(tx)

            if len(self.state.tx_mempool) >= BLOCK_SIZE:
                self.state.persist(self.data_dir)

            return { "message": "Transaction successfully added", "details": f"Awarded {amount} to {to_acc}" if is_reward else f"Transfer {amount} from {from_acc} to {to_acc}" }

        self.sync()

        app.run(port=self.port)