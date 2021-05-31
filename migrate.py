
import json

from database.block import Block, BlockHeader
from database.tx import Tx

new_data = []
with open('./_db/database/block.db') as f:
    for line in f.readlines():
        line_data = json.loads(line)
        new_data.append({ 'time': line_data['block']['header']['time'], 'txs': line_data['block']['txs'] })

new_blocks = []
prev_hash = '00000000000000000000000000000000'
number = 0
for d in new_data:
    block = Block(
        header=BlockHeader(parent=prev_hash, number=number, time=d['time']),
        txs=[Tx.init_from_json(tx) for tx in d['txs']]
    )

    new_blocks.append(block)

    number += 1
    prev_hash = block.create_hash()

with open('./_db/database/new_block.db', 'w') as f:
    for i in range(len(new_blocks)):
        line = json.dumps({ 'hash': new_blocks[i].create_hash(), 'block': new_blocks[i].to_json()})
        if i < len(new_blocks) - 1:
            line += '\n'
        f.write(line)
