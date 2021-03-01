from enum import Enum, auto


class GLibEventSourceEnum(Enum):
    ON_MONITOR_VPN = "on_monitor_vpn"
    ON_MONITOR_NETWORK_SPEED = "on_monitor_network_speed"
    ON_SERVER_LOAD = "on_server_load"


class DashboardFeaturesEnum(Enum):
    KILLSWITCH = 0
    NETSHIELD = 1
    SECURE_CORE = 2


class DashboardKillSwitchIconEnum(Enum):
    OFF = auto()

    ON_DEFAULT = auto()
    ALWAYS_ON_DEFAULT = auto()

    ON_DISABLE = auto()
    ALWAYS_ON_DISABLE = auto()

    ON_ACTIVE = auto()
    ALWAYS_ON_ACTIVE = auto()


class DashboardNetshieldIconEnum(Enum):
    OFF = auto()
    MALWARE_DEFAULT = auto()
    MALWARE_ADS_DEFAULT = auto()

    MALWARE_DISABLE = auto()
    MALWARE_ADS_DISABLE = auto()

    MALWARE_ACTIVE = auto()
    MALWARE_ADS_ACTIVE = auto()


class DashboardSecureCoreIconEnum(Enum):
    OFF = auto()
    ON_DEFAULT = auto()
    ON_DISABLE = auto()
    ON_ACTIVE = auto()
