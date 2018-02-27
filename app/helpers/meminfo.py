import re


class Meminfo:

    def __init__(self, report):
        self.report = report
        self.memfile = report.fullpath.rstrip("/") + "/proc/meminfo"

    def get(self):
        fd = open(self.memfile, "r")
        for l in fd:
            m = re.search("^([^:]+):[\s]+([0-9]+)", l)
            if m:
                setattr(self, m.group(1), int(m.group(2)))
        fd.close()

    def ratio(self, current, total):
        return int(current / total * 100)

    def ratio_mem_used(self):
        if hasattr(self, "MemTotal") is False:
            self.get()
        if self.MemTotal == 0:
            return 0
        return (self.MemTotal - self.MemFree) / float(self.MemTotal) * 100

    def ratio_hugepages_used(self):
        if hasattr(self, "HugePages_Total") is False:
            self.get()
        if self.HugePages_Total == 0:
            return 0
        return (self.HugePages_Total - self.HugePages_Free) / float(self.HugePages_Total) * 100

    def ratio_swap_used(self):
        if hasattr(self, "SwapTotal") is False:
            self.get()
        if self.SwapTotal == 0:
            return 0
        return (self.SwapTotal - self.SwapFree) / float(self.SwapTotal) * 100

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))
