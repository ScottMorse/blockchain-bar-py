"""
Usage:
  main.py (--version | --balances | tx --to=to --amount=amount (--from=from --data=data | --reward))
"""
from docopt import docopt

from cmd.version import describe_version
from cmd.balances import describe_balances
from cmd.tx import add_tx

if __name__ == "__main__":
    args = docopt(__doc__)
    
    for key, val in args.items():
        if isinstance(val, str):
            args[key] = val.strip()

    if args.get('--version'):
        describe_version()
    elif args.get('--balances'):
        describe_balances()
    elif args['tx']:
        add_tx(
            to_acc=args.get('--to'),
            from_acc=args.get('--from'),
            amount=int(args.get('--amount')),
            is_reward=args.get('--reward'),
            data=args.get('--data'),
        )
