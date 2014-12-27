'''
Kea

Usage:
  kea init [--path=.] [--domain=<domain>]
  kea machine list
  kea machine add <name>
  kea machine rm <name>
  kea app list
  kea app add <name>
  kea app rm <name>
  kea --version

Options:
  -h --help                     Show this screen
  --version                     Show version.
  --path=<path>, -p <path>      Speed in knots [default: .].

'''


from docopt import docopt
from kea.cli import Command

def main():
    arguments = docopt(__doc__, version='Kea 0.0.0')
    cmd = Command(arguments)

if __name__ == '__main__':
    main()