import re
class Meminfo:

    def __init__(self, sosreport):
        self.sosreport = sosreport
        self.memfile = sosreport.path.rstrip("/") + "/proc/meminfo"

    def get(self):
        fd = open(self.memfile, "r")
        for l in fd:
            m = re.search("^([^:]+):[\s]+([0-9]+)", l)
            if m:
                setattr(self, m.group(1),m.group(2))
        fd.close()

    def ratio(self, current, total)
        return int(current / total * 100)

    def ratio_mem_used(self):
        return int((self.MemTotal - self.MemFree) / self.MemTotal * 100)

    def ratio_hugepages_used(self):
        return int((self.HugePages_Total - self.HugePages_Free) / self.HugePages_Total * 100)

    def ratio_swap_used(self):
        return int((self.SwapTotal - self.SwapFree) / self.SwapTotal * 100)

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))

    """


        WritebackTmp => '0', 
    SwapTotal => '0', 
    Active(anon) => '25383788', 
    SwapFree => '0', 
    DirectMap4k => '765660', 
    KernelStack => '48480', 
    MemFree => '349488504', 
    HugePages_Rsvd => '0', 
    Committed_AS => '53310264', 
    Active(file) => '6258044', 
    NFS_Unstable => '0', 
    VmallocChunk => '34157088764', 
    Writeback => '0', 
    Inactive(file) => '7164532', 
    MemTotal => '395972536', 
    sosreport => sosreport(
        path => '/cases/02031310/sosreport-20180209-033909/wcmsc5-l-rh-ocld-2'
    ), 
    DirectMap1G => '349175808', 
    memfile => '/cases/02031310/sosreport-20180209-033909/wcmsc5-l-rh-ocld-2/proc/meminfo', 
    AnonHugePages => '8536064', 
    AnonPages => '25890308', 
    Active => '31641832', 
    Inactive(anon) => '29236', 
    CommitLimit => '197986268', 
    Hugepagesize => '2048', 
    Cached => '13501552', 
    SwapCached => '0', 
    VmallocTotal => '34359738367', 
    Dirty => '487712', 
    Mapped => '248316', 
    SUnreclaim => '872968', 
    Unevictable => '560140', 
    SReclaimable => '2046232', 
    VmallocUsed => '1157076', 
    MemAvailable => '363815108', 
    Slab => '2919200', 
    DirectMap2M => '54710272', 
    HugePages_Surp => '0', 
    Bounce => '0', 
    Inactive => '7193768', 
    PageTables => '301184', 
    HardwareCorrupted => '0', 
    HugePages_Total => '0', 
    Mlocked => '560160', 
    HugePages_Free => '0', 
    Buffers => '3500', 
    Shmem => '63460'
    MemTotal — Total amount of physical RAM, in kilobytes.

    MemFree — The amount of physical RAM, in kilobytes, left unused by the system.

    Buffers — The amount of physical RAM, in kilobytes, used for file buffers.

    Cached — The amount of physical RAM, in kilobytes, used as cache memory.

    SwapCached — The amount of swap, in kilobytes, used as cache memory.

    Active — The total amount of buffer or page cache memory, in kilobytes, that is in active use. This is memory that has been recently used and is usually not reclaimed for other purposes.

    Inactive — The total amount of buffer or page cache memory, in kilobytes, that are free and available. This is memory that has not been recently used and can be reclaimed for other purposes.

    HighTotal and HighFree — The total and free amount of memory, in kilobytes, that is not directly mapped into kernel space. The HighTotal value can vary based on the type of kernel used.

    LowTotal and LowFree — The total and free amount of memory, in kilobytes, that is directly mapped into kernel space. The LowTotal value can vary based on the type of kernel used.

    SwapTotal — The total amount of swap available, in kilobytes.

    SwapFree — The total amount of swap free, in kilobytes.

    Dirty — The total amount of memory, in kilobytes, waiting to be written back to the disk.

    Writeback — The total amount of memory, in kilobytes, actively being written back to the disk.

    Mapped — The total amount of memory, in kilobytes, which have been used to map devices, files, or libraries using the mmap command.

    Slab — The total amount of memory, in kilobytes, used by the kernel to cache data structures for its own use.

    Committed_AS — The total amount of memory, in kilobytes, estimated to complete the workload. This value represents the worst case scenario value, and also includes swap memory.

    PageTables — The total amount of memory, in kilobytes, dedicated to the lowest page table level.

    VMallocTotal — The total amount of memory, in kilobytes, of total allocated virtual address space.

    VMallocUsed — The total amount of memory, in kilobytes, of used virtual address space.

    VMallocChunk — The largest contiguous block of memory, in kilobytes, of available virtual address space.

    HugePages_Total — The total number of hugepages for the system. The number is derived by dividing Hugepagesize by the megabytes set aside for hugepages specified in /proc/sys/vm/hugetlb_pool. This statistic only appears on the x86, Itanium, and AMD64 architectures.

    HugePages_Free — The total number of hugepages available for the system. This statistic only appears on the x86, Itanium, and AMD64 architectures.

    Hugepagesize — The size for each hugepages unit in kilobytes. By default, the value is 4096 KB on uniprocessor kernels for 32 bit architectures. For SMP, hugemem kernels, and AMD64, the default is 2048 KB. For Itanium architectures, the default is 262144 KB. This statistic only appears on the x86, Itanium, and AMD64 architectures.
    """