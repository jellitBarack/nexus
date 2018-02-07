class Config(object):
    """
    Common configurations
    """
    APPLICATION_ROOT = "/citellus"
    # Put any configurations here that are common across all environments
    REPORT_FILE_NAMES = ("citellus[0-9]*.json", "magui[0-9]*.json")
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
        "interrupts": { "name": "interupts", "switch": "-I", "label": "intr"},
        "cpu-load": { "name": "CPU Utilization", "switch": "-u", "label": "cpu"},
        "cpu-load-all": { "name": "CPU Utilization", "switch": "-u", "label": "cpu"},
        "io": { "name": "I/O and transfert rates", "switch": "-b"},
        "disk": { "name": "Block devices", "switch": "-d", "label": "disk-device"},
        "filesystem": { "name": "Filesystem", "switch": "-F" },
        "memory": { "name": "Memory", "switch": "-R"},
        "kernel": { "name": "Kernel", "switch": "-v"},
        "hugepages": {"name": "Hugepages", "switch": "-H"},
        "swap-pages": {"name": "Swap pages", "switch": "-W"},
        "swap": { "name": "Swap Utilization", "switch": "-S"},
        "paging": {"name": "Swapping", "switch": "-B"},
        "process-and-context-switch": {"name": "Task Creation and switching", "switch": "-w"},
        "queue": { "name": "Queue Length", "switch": "-q"},
        "network": {
            "is-parent": "true",
            "net-dev": { "name": "Network Devices", "switch": "-n DEV", "label": "iface"},
            "net-edev": { "name": "Network Devices Errors", "switch": "-n EDEV", "label": "iface"},
            "net-nfs": { "name": "NFS Client", "switch": "-n NFS"},
            "net-nfsd":{ "name": "NFS Server", "switch": "-n NFSD"},
            "net-sock": { "name": "SOCK IPv4", "switch": "-n SOCK", "label": "iface"},
            "net-ip": { "name": "IPv4 network traffic", "switch": "-n IP", "label": "iface"},
            "net-eip": { "name": "IPv4 network errors", "switch": "-n EIP", "label": "iface"},
            "net-icmp": { "name": "ICMP IPv4 network traffic", "switch": "-n ICMP", "label": "iface"},
            "net-eicmp": { "name": "ICMP IPv4 network errors", "switch": "-n EICMP", "label": "iface"},
            "net-tcp": { "name": "TCP network traffic", "switch": "-n TCP", "label": "iface"},
            "net-etcp": { "name": "TCP network errors", "switch": "-n ETCP", "label": "iface"},
            "net-udp": { "name": "UDP IPv6 network traffic", "switch": "-n UDP", "label": "iface"},
            "net-ip6": { "name": "IPv6 network traffic", "switch": "-n IP6", "label": "iface"},
            "net-eip6": { "name": "IPv6 network errors", "switch": "-n EIP6", "label": "iface"},
            "net-icmp6": { "name": "ICMP IPv6 network traffic", "switch": "-n ICMP6", "label": "iface"},
            "net-eicmp6": { "name": "ICMP IPv6 network errors", "switch": "-n EICMP6", "label": "iface"},
            "net-sock6": { "name": "SOCK IPv6", "switch": "-n SOCK6", "label": "iface"},
            "net-udp6": { "name": "UDP IPv6 network traffic", "switch": "-n UDP6", "label": "iface"},
            "softnet": { "name": "NFV?", "switch": "-n SOFT", "label": "cpu" }
        },
        "serial": {"name": "Serial"},
        "power-management": {
            "is-parent": "true",
            "cpu-frequency": { "name": "CPU Clock frequency", "switch": "-m FREQ", "label": "number" },
            "fan-speed": { "name": "FAN RPM", "switch": "-m FAN", "label": "number" },
            "usb-devices": { "name": "CPU Clock frequency", "switch": "-m USB" },
            "voltage-input": { "name": "Input Power", "switch": "-m IN", "label": "number" },
            "temperature": { "name": "Temperature", "switch": "-m TEMP", "label": "number" },
        }
    }
    # we need to disable CSRF for the search form at the top
    WTF_CSRF_ENABLED=False


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False
    SQLALCHEMY_ECHO = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
