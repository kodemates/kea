from . import Config


class Command(object):

    def build_kwargs(self):
        kwargs = dict()
        for k in self.arguments:
            if k[:2] == '--' and self.arguments[k]:
                kwargs[k[2:]] = self.arguments[k]
        return kwargs

    def has(self, key):
        return key in self.arguments and self.arguments[key]

    def list(self, items):
        for x in items:
            print("{}\t{}".format(x, items[x]))

    def __init__(self, arguments):
        self.arguments = arguments
        config = Config()
        kwargs = self.build_kwargs()

        if self.has('init'):
            config.init(**kwargs)
            return

        config.load_config(**kwargs)

        if self.has('machine'):
            if self.has('list'):
                self.list(config.list_machines())
            elif self.has('add'):
                config.add_machine(self.arguments['<name>'], **kwargs)
                config.save_config()
            elif self.has('rm'):
                config.remove_machine(self.arguments['<name>'])
                config.save_config()


        if self.has('app'):
            if self.has('list'):
                self.list(config.list_apps())
            elif self.has('add'):
                config.add_app(self.arguments['<name>'], **kwargs)
                config.save_config()
            elif self.has('rm'):
                config.remove_app(self.arguments['<name>'])
                config.save_config()


