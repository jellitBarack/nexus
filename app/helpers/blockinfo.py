import re
class Blocks:
    data_table = {}
    def __init__(self):
        return


class Blockinfo(Blocks):
    io_names = [ "reads_completed", "reads_merged", "sectors_read",
                "reading_ms", "writes_completed", "writes_merged",
                "writing_ms", "io_in_progress", "io_ms", "io_weighted" ]
    def __init__(self, sosreport):
        self.sosreport = sosreport
        self.dfblock = sosreport.path.rstrip("/") + "/sos_commands/filesys/df_-al"
        self.dfinode = sosreport.path.rstrip("/") + "/sos_commands/filesys/df_-ali"
        self.iostat =  sosreport.path.rstrip("/") + "/proc/diskstats"

    def get_list_io(self):
        file = self.iostat
        io = self.match_line("io", file, "[0-9\s]+([^0-9\s]+)[\s]+(.*)")
        return io

    def get_list_block(self):
        file = self.dfblock
        blocks = self.match_line("block", file, 
                            "^/dev/([^\s]+)[\s]+([0-9]+)[\s]+([0-9]+)[\s]+([0-9]+)[\s]+([0-9]+)\%[\s]+(.*)")
        return blocks

    def get_list_inode(self):
        file = self.dfinode
        inodes = self.match_line("inode", file, 
                            "^/dev/([^\s]+)[\s]+([0-9]+)[\s]+([0-9]+)[\s]+([0-9]+)[\s]+([0-9]+)\%[\s]+(.*)")
        return inodes

    def get_device(self, device_name):
        try:
            self = self.data_table[device_name]
        except KeyError:
             self.device_name = device_name
             self.data_table[device_name] = self
        return self
    
    def match_line(self, type, file, regex):
        fd = open(file, "r")
        for l in fd:
            m = re.search(regex, l)
            if m:
                block_device = self.get_device(m.group(1))
                if (type == "io"):
                    for k, v in dict(zip(block_device.io_names, m.group(2).split())).iteritems():
                        setattr(block_device, k, v)
                        
                else:
                    block_device.total = m.group(2)
                    block_device.used = m.group(3)
                    block_device.free = m.group(4)
                    block_device.percent = m.group(5)
                    block_device.mountpoint = m.group(6)
                self.data_table[block_device.device_name] = block_device
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


class Iostats(Blockinfo):
    def __init__(self, file, regex):
        Parent.__init__(self)


class Bockstats(Blockinfo):
   def __init__(self):
        Parent.__init__(self)

class Inodestats(Blockinfo):
   def __init__(self):
        Parent.__init__(self)

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
