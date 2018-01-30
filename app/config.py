class Config(object):
    """
    Common configurations
    """
    APPLICATION_ROOT = "/citellus"
    # Put any configurations here that are common across all environments
    REPORT_FILE_NAMES = ("citellus.json", "magui.json")
    CITELLUS_PATH = "/git/citellus"
    RC_OKAY = 10
    RC_FAILED = 20
    RC_SKIPPED = 30
    PLUGIN_STATES = { 
        10: { 
            "icon": "fa fa-check-circle-o",
            "state": "okay",
            "hclass": "success",
            "text_color": "text-black"
        },
        20: { 
            "icon": "pficon pficon-error-circle-o",
            "state": "failed",
            "hclass": "danger",
            "text_color": "text-black"
        },
        30: { 
            "icon": "pficon pficon-help",
            "state": "skipped",
            "hclass": "info",
            "text_color": "text-black"
        }
    }
    # SADF binary: On RHEL7, you need to have a sysstat-10 parse
    SYSSTAT_SADF = "/var/www/citellus/bin/sadf"
    # Number of days we look in the past by default when graphing
    SYSSTAT_DEFAULT_DAYS = 365
    # List of activities with a description and the switch to pass to sadf to get the data
    SYSSTAT_ACTIVITIES = {
        "INT": { "name": "interupts", "switch": "-I"},
        "CPU": { "name": "CPU Utilization", "switch": "-u"},
        "SWAP": { "name": "Swap Utilization", "switch": "-S"},
        "PAGE": { "name": "paging", "switch": "-B"},
        "IO": { "name": "I/O and transfert rates", "switch": "-b"},
        "DISK": { "name": "Block devices", "switch": "-d" },
        "XDISK": { "name": "Filesystem", "switch": "-F" },
        "MEMORY": { "name": "Memory", "switch": "-R"},
        "MEMORY_UTIL": { "name": "Memory Utilization", "switch": "-r"},
        "HUGE": {"name": "Hugepages", "switch": "-H"},
        "INODES": {"name": "Inodes", "switch": "-v"},
        "SWAPPING": {"name": "Swapping", "switch": "-w"},
        "PCSW": {"name": "Task Creation and switching", "switch": "-w"},
        "QUEUE": { "name": "Queue Length", "switch": "-q"},
        "NET_DEV": { "name": "Network Devices", "switch": "-n DEV"},
        "NET_EDEV": { "name": "Network Devices Errors", "switch": "-n EDEV"},
        "NET_NFS": { "name": "NFS Client", "switch": "-n NFS"},
        "NET_NFSD":{ "name": "NFS Server", "switch": "-n NFSD"},
        "NET_SOCK": { "name": "SOCK IPv4", "switch": "-n SOCK"},
        "NET_IP": { "name": "IPv4 network traffic", "switch": "-n IP"},
        "NET_EIP": { "name": "IPv4 network errors", "switch": "-n EIP"},
        "NET_ICMP": { "name": "ICMP IPv4 network traffic", "switch": "-n ICMP"},
        "NET_EICMP": { "name": "ICMP IPv4 network errors", "switch": "-n EICMP"},
        "NET_TCP": { "name": "TCP network traffic", "switch": "-n TCP"},
        "NET_TCP": { "name": "TCP network errors", "switch": "-n ETCP"},
        "NET_UDP": { "name": "UDP IPv6 network traffic", "switch": "-n UDP"},
        "NET_IP6": { "name": "IPv6 network traffic", "switch": "-n IP6"},
        "NET_EIP6": { "name": "IPv6 network errors", "switch": "-n EIP6"},
        "NET_ICMP6": { "name": "ICMP IPv6 network traffic", "switch": "-n ICMP6"},
        "NET_EICMP6": { "name": "ICMP IPv6 network errors", "switch": "-n EICMP6"},
        "NET_SOCK6": { "name": "SOCK IPv6", "switch": "-n SOCK6"},
        "NET_UDP6": { "name": "UDP IPv6 network traffic", "switch": "-n UDP6"},
        "PwR_CPU": { "name": "CPU Power", "switch": "-m CPU" },
        "PwR_FAN": { "name": "FAN RPM", "switch": "-m FAN" },
        "PwR_FREQ": { "name": "CPU Clock frequency", "switch": "-m FREQ" },
        "PwR_IN": { "name": "Input Power", "switch": "-m IN" },
        "PwR_TEMP": { "name": "Temperature", "switch": "-m TEMP" },
    }
    # we need to disable CSRF for the search form at the top
    WTF_CSRF_ENABLED=False


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
