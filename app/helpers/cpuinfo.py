import re

class Cpuinfo:
    cpu_stat_names = [ "user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal", "guest", "guest_nice" ]

    def __init__(self, sosreport):
        self.sosreport = sosreport
        self.cpustat = sosreport.path.rstrip("/") + "/proc/stat"

    def get(self):
        fd = open(self.cpustat, "r")
        for l in fd:
            m = re.search("^cpu[\s]+(.*)", l)
            if m:
                time_total = 0
                for k, v in dict(zip(self.cpu_stat_names, m.group(1).split())).iteritems():
                    setattr(self, k, v)
                    time_total += int(v)
                self.time_total = time_total
        fd.close()

    def get_ratio(self, key):
        cycles = int(getattr(self, key))
        return round(float(cycles) / float(self.time_total) * 100, 2)

    def get_all_ratios(self):
        ratios = {}
        for s in self.cpu_stat_names:
            ratios[s] = self.get_ratio(s)

        return ratios

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))