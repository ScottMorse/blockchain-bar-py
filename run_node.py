"""
Usage:
  run_node.py [--port=<port> | --bootstrap]
"""
from docopt import docopt

from node import Node, PeerNode

BOOTSTRAP_PORT = 1111

if __name__ == "__main__":
    args = docopt(__doc__)

    is_bootstrap = args.get('--bootstrap')
    port = args.get('--port')

    if is_bootstrap:
        node = Node(data_dir="./_db", port=BOOTSTRAP_PORT, bootstrap_node=None, is_bootstrap=True)
    else:
        bootstrap = PeerNode(ip='127.0.0.1', port=BOOTSTRAP_PORT, is_bootstrap=True, is_active=True)
        
        node = Node(data_dir="./_db", port=port if port else 8080, bootstrap_node=bootstrap)

    node.run()