from dataclasses import dataclass
from enum import auto

from ...enums import (DashboardKillSwitchIconEnum, DashboardNetshieldIconEnum,
                      DashboardSecureCoreIconEnum)


@dataclass
class Loading:
    pass


@dataclass
class ConnectError:
    message: str
    display_troubleshoot_dialog: bool


@dataclass
class ConnectPreparingInfo:
    pass


@dataclass
class ConnectInProgressInfo:
    entry_country: str
    exit_country: str
    city: str
    servername: str
    protocol: str
    is_secure_core: bool


@dataclass
class ConnectedToVPNInfo:
    servername: str
    city: str
    countries: list
    protocol: str
    ip: str
    load: str
    entry_country_code: str
    exit_country_code: str


@dataclass
class NetworkSpeed:
    upload: str
    download: str


@dataclass
class NotConnectedToVPNInfo:
    ip: str
    isp: str
    country: str
    perma_ks_enabled: bool


@dataclass
class ServerListData:
    server_list: list
    display_secure_core: bool


@dataclass
class SwitchServerList:
    display_secure_core: bool


@dataclass
class QuickSettingsStatus:
    secure_core: DashboardSecureCoreIconEnum
    netshield: DashboardNetshieldIconEnum
    killswitch: DashboardKillSwitchIconEnum


@dataclass
class DisplayDialog:
    title: str
    text: str


@dataclass
class DisplayEvent:
    event_dataclass: auto()
    has_notification_been_opened: bool
    set_notification_as_read: auto()  # method callback


@dataclass
class BlackFridayEvent:
    class_instance: auto()
