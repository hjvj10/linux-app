import threading
import time
from dataclasses import dataclass

import psutil
from protonvpn_nm_lib import exceptions
from protonvpn_nm_lib.constants import VIRTUAL_DEVICE_NAME
from protonvpn_nm_lib.enums import (ConnectionMetadataEnum,
                                    ConnectionStatusEnum, ConnectionTypeEnum,
                                    DbusMonitorResponseEnum,
                                    DbusVPNConnectionReasonEnum,
                                    DbusVPNConnectionStateEnum, FeatureEnum,
                                    NetworkManagerConnectionTypeEnum)
from rx.subject.replaysubject import ReplaySubject


@dataclass
class Loading:
    pass


@dataclass
class ConnectError:
    message: str


@dataclass
class ConnectPreparingInfo:
    pass


@dataclass
class ConnectInProgressInfo:
    country: str
    city: str
    servername: str
    protocol: str


@dataclass
class ConnectedToVPNInfo:
    servername: str
    city: str
    countries: list
    protocol: str
    ip: str
    load: str
    country_code: str


@dataclass
class NetworkSpeed:
    upload: str
    download: str


@dataclass
class NotConnectedToVPNInfo:
    ip: str


class DashboardViewModel:
    _thread_list = []
    _conn_state_msg = {
        DbusVPNConnectionStateEnum.UNKNOWN: "State of "
        "VPN connection is unkown.",
        DbusVPNConnectionStateEnum.NEEDS_CREDENTIALS: "The VPN "
        "connection is missing credentials.",
        DbusVPNConnectionStateEnum.FAILED: "Failed to "
        "connect to VPN.",
        DbusVPNConnectionStateEnum.DISCONNECTED: "VPN connection "
        "has been disconnected.",
        DbusVPNConnectionStateEnum.UNKNOWN_ERROR: "Unknown error."
    }

    _conn_reason_msg = {
        DbusVPNConnectionReasonEnum.UNKNOWN: "The reason for the active "
        "connection state change is unknown.",
        DbusVPNConnectionReasonEnum.NOT_PROVIDED: "No reason was given "
        "for the active connection state change.",
        DbusVPNConnectionReasonEnum.USER_HAS_DISCONNECTED: "The active "
        "connection changed state because the user "
        "disconnected it.",
        DbusVPNConnectionReasonEnum.DEVICE_WAS_DISCONNECTED: "The active "
        "connection changed state because the device it was using "
        "was disconnected.",
        DbusVPNConnectionReasonEnum.SERVICE_PROVIDER_WAS_STOPPED: "The "
        "service providing the VPN connection was stopped.",
        DbusVPNConnectionReasonEnum.IP_CONFIG_WAS_INVALID: "The IP "
        "configuration of the active connection is invalid.",
        DbusVPNConnectionReasonEnum.CONN_ATTEMPT_TO_SERVICE_TIMED_OUT: "The "
        "connection attempt to the VPN service timed out.",
        DbusVPNConnectionReasonEnum.TIMEOUT_WHILE_STARTING_VPN_SERVICE_PROVIDER: # noqa
        "A timeout occurred while starting the service providing "
        "the VPN connection.",
        DbusVPNConnectionReasonEnum.START_SERVICE_VPN_CONN_SERVICE_FAILED:
        "Starting the service providing the VPN connection failed.",
        DbusVPNConnectionReasonEnum.SECRETS_WERE_NOT_PROVIDED: "Necessary "
        "secrets for the connection were not provided.",
        DbusVPNConnectionReasonEnum.SERVER_AUTH_FAILED: "Authentication "
        "to the server failed.",
        DbusVPNConnectionReasonEnum.DELETED_FROM_SETTINGS: "The connection "
        "was deleted from settings.",
        DbusVPNConnectionReasonEnum.MASTER_CONN_FAILED_TO_ACTIVATE: "Master "
        "connection failed to activate.",
        DbusVPNConnectionReasonEnum.CREATE_SOFTWARE_DEVICE_LINK_FAILED:
        "Could not create the software device link.",
        DbusVPNConnectionReasonEnum.VPN_DEVICE_DISAPPEARED: "The device this "
        "connection depended on disappeared.",
        DbusVPNConnectionReasonEnum.UNKNOWN_ERROR: "Unknown reason occured."
    }

    def __init__(self, protonvpn, dashboard_model):
        self.protonvpn = protonvpn
        self.dashboard_model = dashboard_model
        self.state = ReplaySubject(buffer_size=1)

    def on_startup(self):
        self.state.on_next(Loading())
        thread = threading.Thread(
            target=self.thread_on_startup
        )
        thread.daemon = True
        thread.start()
        return False

    def thread_on_startup(self):
        try:
            self.protonvpn._ensure_connectivity()
        except (exceptions.ProtonVPNException, Exception):
            # loggger.exception
            result = NotConnectedToVPNInfo(
                ip=None
            )
            self.state.on_next(result)
            return

        if len(self.protonvpn._get_protonvpn_connection(
            NetworkManagerConnectionTypeEnum.ACTIVE
        )) < 1:
            result = self.set_not_connected_state()
        else:
            result = self.set_connected_state()

        self.state.on_next(result)

    def on_quick_connect(self):
        result = ConnectPreparingInfo()
        self.state.on_next(result)
        self.connect(ConnectionTypeEnum.FASTEST)
        return False

    def connect(self, connection_type_enum):
        try:
            response = self.protonvpn._setup_connection(
                connection_type_enum
            )
        except (exceptions.ProtonVPNException, Exception) as e:
            result = ConnectError(
                str(e)
            )
            self.state.on_next(result)
            return

        # step 1
        servername = response[ConnectionMetadataEnum.SERVER.value]
        protocol = response[ConnectionMetadataEnum.PROTOCOL.value]
        server_info = self.protonvpn._get_server_information(servername)
        result = ConnectInProgressInfo(
            country=server_info.COUNTRY,
            city=server_info.CITY,
            servername=servername,
            protocol=protocol.upper()
        )

        self.state.on_next(result)

        # step 2
        respone = self.protonvpn._connect()
        try:
            state = respone[DbusMonitorResponseEnum.STATE]
        except TypeError as e:
            result = ConnectError(
                str(e)
            )
            self.state.on_next(result)
            return

        # step 3
        if state == DbusVPNConnectionStateEnum.IS_ACTIVE:
            result = self.set_connected_state()
        else:
            result = ConnectError(
                self._conn_reason_msg[respone[DbusMonitorResponseEnum.REASON]]
            )

        self.state.on_next(result)

    def on_disconnect(self):
        result = self.set_not_connected_state()
        try:
            self.protonvpn._disconnect()
        except exceptions.ConnectionNotFound:
            pass

        self.state.on_next(result)
        return False

    def set_connected_state(self):
        connection_status = self.protonvpn._get_active_connection_status(False)
        server_info = connection_status[
            ConnectionStatusEnum.SERVER_INFORMATION
        ]

        countries = [server_info.COUNTRY]
        if FeatureEnum.SECURE_CORE in server_info.FEATURE_LIST:
            countries.append(server_info.ENTRY_COUNTRY)

        result = ConnectedToVPNInfo(
            protocol=connection_status[ConnectionStatusEnum.PROTOCOL],
            servername=server_info.SERVERNAME,
            countries=countries,
            city=server_info.CITY,
            ip=connection_status[ConnectionStatusEnum.SERVER_IP],
            load=str(server_info.LOAD),
            country_code="server_info.COUNTRY"
        )

        return result

    def set_not_connected_state(self):
        result = NotConnectedToVPNInfo(
            ip=self.dashboard_model.get_ip()
        )

        return result

    def on_monitor_vpn(self):
        thread = threading.Thread(
            target=self.thread_on_startup
        )
        thread.daemon = True
        thread.start()
        return True

    def thread_on_monitor_vpn(self):
        protonvpn_connection = self.protonvpn._get_protonvpn_connection(
            NetworkManagerConnectionTypeEnum.ACTIVE
        )
        if len(protonvpn_connection) < 1:
            result = self.set_not_connected_state()

            self.state.on_next(result)
        return True

    def on_update_server_load(self):
        thread = threading.Thread(
            target=self.thread_on_update_server_load
        )
        thread.daemon = True
        thread.start()
        return True

    def thread_on_update_server_load(self):
        try:
            self.protonvpn._refresh_servers()
        except Exception as e: # noqa
            # logger.exception(e)
            pass

        result = self.set_connected_state()

        self.state.on_next(result)
        return True

    def on_update_speed(self):
        thread = threading.Thread(
            target=self.thread_on_update_speed
        )
        thread.daemon = True
        thread.start()
        return True

    def thread_on_update_speed(self):
        speed_result = self.on_calculate_speed()
        up, dl = "-", "-"
        if len(speed_result) == 2:
            up, dl = str(speed_result[0]), str(speed_result[1])
        result = NetworkSpeed(
            download=dl,
            upload=up
        )

        self.state.on_next(result)
        return True

    def on_calculate_speed(self):
        t0 = time.time()
        interface = VIRTUAL_DEVICE_NAME
        dt = 1
        try:
            counter = psutil.net_io_counters(pernic=True)[interface]
        except KeyError:
            return []
        tot = (counter.bytes_sent, counter.bytes_recv)

        last_tot = tot
        time.sleep(dt)
        try:
            counter = psutil.net_io_counters(pernic=True)[interface]
        except KeyError:
            return []

        t1 = time.time()
        tot = (counter.bytes_sent, counter.bytes_recv)
        ul, dl = [
            (now - last) / (t1 - t0)
            for now, last
            in zip(tot, last_tot)
        ]
        return [round(ul), round(dl)]
