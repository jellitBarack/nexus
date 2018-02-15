class Sosreport:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))