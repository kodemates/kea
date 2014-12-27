'''
Kea: Platform as a service
In early development

Usage:
  kea init
  kea machine list
  kea machine add <name>
  kea machine rm <name>
  kea app list
  kea app add <name>
  kea app rm <name>
  kea --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.

'''


from docopt import docopt

def main():
    arguments = docopt(__doc__, version='Kea 0.0')
    print(arguments)

if __name__ == '__main__':
    main()