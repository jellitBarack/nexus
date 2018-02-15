
from sosreport import Sosreport
from cpuinfo import Cpuinfo

s = Sosreport("/cases/02031310/sosreport-20180209-033909/wcmsc5-l-rh-ocld-2")

"""
m = Cpuinfo(s)
m.get()
print(m.get_all_ratios())
"""

print(m)
