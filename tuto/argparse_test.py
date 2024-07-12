import argparse
parser = argparse.ArgumentParser(prog='PROG')
parser.add_argument('--foo', required=True, help='foo help')
subparsers = parser.add_subparsers(help='sub-command help')

# create the parser for the "bar" command
parser_a = subparsers.add_parser('bar', help='a help')
parser_a.add_argument('bar', type=int, help='bar help')
print(parser.parse_args())