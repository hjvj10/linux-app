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

from ..logger import logger


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
    """Dashboard View Model.

    Uses the protonvpn library to take different actions.
    It uses the state variable to notify the View (which is
    listening and awaiting for any changes), to update the UI
    accordingly.

    Due to the fact that the protonvpn library uses GLib (which
    the UI is also running on) to add, start, remove and stop
    connections it is currently no possible to execute these
    in a thread to make the UI more fluid. Thus, the main thread
    is passed back and forth (from library to UI and vice-versa)
    to execute these processes. Thus, whenever possible, python threads
    are used so that the UI changes are more fluid.

    All threads should run in daemon mode, so that when the program is closed,
    all threads are also closed.
    """

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

    one_byte_in_kBs = 0.000976
    one_byte_in_mBs = 9.76e-7
    one_kilobyte_in_bytes = 1000
    one_megabyte_in_bytes = 1024590.163934

    def __init__(self, protonvpn, dashboard_model):
        self.protonvpn = protonvpn
        self.dashboard_model = dashboard_model
        self.state = ReplaySubject(buffer_size=1)

    def on_startup(self):
        """On startup method.

        This method is invoked once the application window is started.
        It displays a loading screen and then invokes a python thread
        so that the animiation does not stopped during this loading state.
        """
        self.state.on_next(Loading())
        thread = threading.Thread(
            target=self.thread_on_startup
        )
        thread.daemon = True
        thread.start()

    def thread_on_startup(self):
        """Threaded method.

        This method should be started within a python thread,
        so that the UI is fluid and does not freeze the main
        thread, due protonvpn library (described in class docstring).

        This class updates the UI state accordingly.
        """
        try:
            self.protonvpn._ensure_connectivity()
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = NotConnectedToVPNInfo(
                ip=None
            )
            self.state.on_next(result)
            return

        if len(self.protonvpn._get_protonvpn_connection(
            NetworkManagerConnectionTypeEnum.ACTIVE
        )) < 1:
            result = self.get_not_connected_state()
        else:
            result = self.get_connected_state()

        self.state.on_next(result)

    def on_quick_connect(self):
        """On quick connect method. Proxymethod to connect.

        This method sets the state of the UI
        to preparing and calls the method
        connect() with ConnectionTypeEnum type.

        Ideally the on_quick_connect() method should be run
        within a python thread. Due to current situation, it is
        not done so due the reasons specified in class docstring.
        """
        result = ConnectPreparingInfo()
        self.state.on_next(result)
        self.connect(ConnectionTypeEnum.FASTEST)

    def connect(self, connection_type_enum):
        """General connect method.

        This method should always be used when connecting to
        VPN. Ideally should be run within a python thread.

        It initially attemps to setup the connection, then updated
        the UI accordingly and only the proceeds to connect to the VPN.
        This is done so that the user is aware of where the connections
        is made to during the ConnectInProgressInfo() state.

        Args:
            connection_type_enum (ConnectionTypeEnum)
        """
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
            result = self.get_connected_state()
        else:
            result = ConnectError(
                self._conn_reason_msg[respone[DbusMonitorResponseEnum.REASON]]
            )

        self.state.on_next(result)

    def on_disconnect(self):
        """On disconnect method.

        Ideally the on_disconnect() method should be run
        within a python thread, but is not done so due to
        the reasons specified in class docstring.
        """
        result = self.get_not_connected_state()
        try:
            self.protonvpn._disconnect()
        except exceptions.ConnectionNotFound:
            pass

        self.state.on_next(result)
        return False

    def get_connected_state(self):
        """Get connected state.

        Returns:
            ConnectedToVPNInfo
        """
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

    def get_not_connected_state(self):
        """Get not connected state.

        Returns:
            ConnectedToVPNInfo
        """
        result = NotConnectedToVPNInfo(
            ip=self.dashboard_model.get_ip()
        )

        return result

    def on_monitor_vpn(self):
        """Start VPN connection monitor.

        Since the VPN can be enabled via CLI,
        it should constantly monitor for an active
        protonvpn connection created by the library.

        The main method is started within a python thread
        so that the UI does not freeze up.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        thread = threading.Thread(
            target=self.thread_on_startup
        )
        thread.daemon = True
        thread.start()
        return True

    def thread_on_monitor_vpn(self):
        """Monitor VPN connection.

        This methods monitors a VPN connection state from withing
        a thread. It is mainly used to track when a VPN connection
        is stopped and/or removed.
        """
        protonvpn_connection = self.protonvpn._get_protonvpn_connection(
            NetworkManagerConnectionTypeEnum.ACTIVE
        )
        if len(protonvpn_connection) < 1:
            result = self.get_not_connected_state()

            self.state.on_next(result)

    def on_update_server_load(self):
        """Update server Load.

        The main method is started within a python thread
        so that the UI does not freeze up.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        thread = threading.Thread(
            target=self.thread_on_update_server_load
        )
        thread.daemon = True
        thread.start()
        return True

    def thread_on_update_server_load(self):
        """Update server load.

        This metho actually refresh server cache. The library
        will automatically decide what it should cache, so this
        method can be safely used at anytime.

        This method is and should be executed within a python thread.
        """
        try:
            self.protonvpn._refresh_servers()
        except Exception as e:
            logger.exception(e)

        result = self.get_connected_state()

        self.state.on_next(result)

    def on_update_speed(self):
        """Update network speed.

        The main method is started within a python thread
        so that the UI does not freeze up.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        thread = threading.Thread(
            target=self.thread_on_update_speed
        )
        thread.daemon = True
        thread.start()
        return True

    def thread_on_update_speed(self):
        """Updates UI with current network speed.

        This method is and should be executed within a python thread,
        so that it does not freeze the UI due to the constant
        UI updates.
        """
        speed_result = self.get_network_speed()
        up, dl = "-", "-"
        if len(speed_result) == 2:
            up, dl = str(speed_result[0]), str(speed_result[1])
        result = NetworkSpeed(
            download=dl,
            upload=up
        )

        self.state.on_next(result)

    def get_network_speed(self):
        """Get current network speed.

        It searches for a interface that is defined within the library.

        Returns:
            list
        """
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
        ul = self.convert_network_speed(ul)
        dl = self.convert_network_speed(dl)

        return [ul, dl]

    def convert_network_speed(self, byte_per_second):
        """Convert network speed.

        Converts and return
        the speed  easy readeable units:
            - Bytes per second
            - Kilobytes per second
            - Megabytes per second

        Args:
            byte_per_second(int|float)

        Returns:
            string
        """
        if (
            byte_per_second >= self.one_kilobyte_in_bytes
            and byte_per_second < self.one_megabyte_in_bytes
        ):
            return str(
                round((byte_per_second * self.one_byte_in_kBs), 1)
            ) + " KB/s"
        elif byte_per_second >= self.one_megabyte_in_bytes:
            return str(
                round((byte_per_second * self.one_byte_in_mBs), 1)
            ) + " MB/s"
        else:
            return str(int(byte_per_second)) + " B/s"
