import re
class Blocks:
    data_table = {}

    def __init__(self, report):
        self.report = report
        self.dfblock = report.fullpath.rstrip("/") + "/sos_commands/filesys/df_-al"
        self.dfinode = report.fullpath.rstrip("/") + "/sos_commands/filesys/df_-ali"
        self.iostat =  report.fullpath.rstrip("/") + "/proc/diskstats"

    def get_device(self, device_name, file_type):
        try:
            device = self.data_table[device_name]
        except KeyError:
            self.data_table[device_name] = {}

        try:
            device = self.data_table[device_name][file_type]
        except KeyError:
            if file_type == "io":
                self.data_table[device_name][file_type] = Iostats(device_name)
            elif file_type == "block":
                self.data_table[device_name][file_type] = Blockstats(device_name)
            elif file_type == "inode":
                self.data_table[device_name][file_type] = Inodestats(device_name)

        return self.data_table[device_name][file_type]

    def match_line(self, file_type, file_name, regex):
        fd = open(file_name, "r")
        for l in fd:
            m = re.search(regex, l)
            if m:
                block_device = self.get_device(m.group(1), file_type)
                if file_type == "io":
                    for k, v in dict(zip(block_device.io_names, m.group(2).split())).iteritems():
                        setattr(block_device, k, int(v))

                else:
                    setattr(block_device, "total", int(m.group(2)))
                    setattr(block_device, "used", int(m.group(3)))
                    setattr(block_device, "free", int(m.group(4)))
                    setattr(block_device, "percent", int(m.group(5)))
                    if hasattr(block_device, "mountpoint") is False:
                        setattr(block_device, "mountpoint", m.group(6))
                self.data_table[block_device.device_name][file_type] = block_device
        fd.close()

    def list_io(self):
        self.match_line("io", self.iostat, "[0-9]+[\s]+[0-9]+[\s]+([^0-9\s]+[0-9]*)[\s]+(.*)")

    def list_block_space(self):
        self.match_line("block", self.dfblock, "^/dev/([^\s]+)[\s]+([0-9]+)[\s]+([0-9]+)[\s]+([0-9]+)[\s]+([0-9]+)\%[\s]+(.*)")

    def list_inode_space(self):
        self.match_line("inode", self.dfinode, "^/dev/([^\s]+)[\s]+([0-9]+)[\s]+([0-9]+)[\s]+([0-9]+)[\s]+([0-9]+)\%[\s]+(.*)")

    def get_ratio(self, key):
        cycles = int(getattr(self, key))
        return round(float(cycles) / float(self.time_total) * 100, 2)

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))


class Blockinfo(Blocks):
    io_names = [ "reads_completed", "reads_merged", "sectors_read",
                "reading_ms", "writes_completed", "writes_merged",
                "writing_ms", "io_in_progress", "io_ms", "io_weighted" ]

    def dump(self):
        out = {}
        for (k,v) in vars(self).items():
            out[k] = v
        return out

    def __init__(self, device_name):
        self.device_name = device_name

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))


class Iostats(Blockinfo):

    def __init__(self, device_name):
        self.device_name = device_name

class Blockstats(Blockinfo):

   def __init__(self, device_name):
        self.device_name = device_name

class Inodestats(Blockinfo):

   def __init__(self, device_name):
        self.device_name = device_name

"""
Field  1 -- # of reads completed
    This is the total number of reads completed successfully.

Field  2 -- # of reads merged, field 6 -- # of writes merged
    Reads and writes which are adjacent to each other may be merged for
    efficiency.  Thus two 4K reads may become one 8K read before it is
    ultimately handed to the disk, and so it will be counted (and queued)
    as only one I/O.  This field lets you know how often this was done.

Field  3 -- # of sectors read
    This is the total number of sectors read successfully.

Field  4 -- # of milliseconds spent reading
    This is the total number of milliseconds spent by all reads (as
    measured from __make_request() to end_that_request_last()).

Field  5 -- # of writes completed
    This is the total number of writes completed successfully.

Field  6 -- # of writes merged
    See the description of field 2.

Field  7 -- # of sectors written
    This is the total number of sectors written successfully.

Field  8 -- # of milliseconds spent writing
    This is the total number of milliseconds spent by all writes (as
    measured from __make_request() to end_that_request_last()).

Field  9 -- # of I/Os currently in progress
    The only field that should go to zero. Incremented as requests are
    given to appropriate struct request_queue and decremented as they finish.

Field 10 -- # of milliseconds spent doing I/Os
    This field increases so long as field 9 is nonzero.

Field 11 -- weighted # of milliseconds spent doing I/Os
    This field is incremented at each I/O start, I/O completion, I/O
    merge, or read of these stats by the number of I/Os in progress
    (field 9) times the number of milliseconds spent doing I/O since the
    last update of this field.  This can provide an easy measure of both
    I/O completion time and the backlog that may be accumulating.
"""
