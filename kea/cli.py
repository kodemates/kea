from . import Config

class Command(object):

    def build_kwargs(self, arguments):
        kwargs = dict()
        for k in arguments:
            if k[:2] == '--' and arguments[k]:
                kwargs[k[2:]] = arguments[k]
        return kwargs


    def __init__(self, arguments):
        if 'init' in arguments:
            config = Config()
            kwargs = self.build_kwargs(arguments)
            config.init(**kwargs)



