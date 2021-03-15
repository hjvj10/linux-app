from dataclasses import dataclass

from protonvpn_nm_lib import exceptions
from protonvpn_nm_lib.enums import (ConnectionMetadataEnum,
                                    ConnectionStatusEnum, ConnectionTypeEnum,
                                    DbusMonitorResponseEnum,
                                    DbusVPNConnectionReasonEnum,
                                    DbusVPNConnectionStateEnum, FeatureEnum)
from ..rx.subject.replaysubject import ReplaySubject
from ..model.dashboard_connect_list import DashboardConnectList

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


class DashboardViewModel:
    """Dashboard View Model.

    Uses the protonvpn library to take different actions.
    It uses the state variable to notify the View (which is
    listening and awaiting for any changes), to update the UI
    accordingly.

    Due to the fact that the protonvpn library uses GLib (which
    the UI is also running on) to add, start, remove and stop
    connections it is currently no possible to execute these
    in a thread/background to make the UI more fluid. Thus, the main thread
    is passed back and forth (from library to UI and vice-versa)
    to execute these processes. Thus, whenever possible, python threads
    are used so that the UI changes are more fluid.

    All threads should run in daemon mode, so that when the program is closed,
    all threads are also closed.
    """

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

    def __init__(
        self, protonvpn, utils,
        bg_process, dashboard_connect_list=DashboardConnectList()
    ):
        self.protonvpn = protonvpn
        self.utils = utils
        self.bg_process = bg_process
        self.dashboard_connect_list = dashboard_connect_list
        self.state = ReplaySubject(buffer_size=1)

    def on_startup(self):
        """On startup method.

        This method is invoked once the application window is started.
        It displays a loading screen and then invokes a python thread
        so that the animiation does not stopped during this loading state.
        """
        self.state.on_next(Loading())
        process = self.bg_process.setup_no_params(self.on_startup_sync)
        process.start()

    def on_startup_sync(self):
        """Threaded method.

        This method should be started within a python thread,
        so that the UI is fluid and does not freeze the main
        thread, due protonvpn library (described in class docstring).

        This class updates the UI state accordingly.
        """
        try:
            self.protonvpn.ensure_connectivity()
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = NotConnectedToVPNInfo(
                ip=None,
                isp=None,
                country=None
            )
            self.state.on_next(result)
            return

        if not self.protonvpn.get_active_protonvpn_connection():
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
            server = self.protonvpn.setup_connection(
                connection_type_enum
            )
        except (exceptions.ProtonVPNException, Exception) as e:
            result = ConnectError(
                str(e)
            )
            self.state.on_next(result)
            return

        # step 1
        connection_metadata = self.protonvpn.get_connection_metadata()
        protocol = connection_metadata[ConnectionMetadataEnum.PROTOCOL.value]
        result = ConnectInProgressInfo(
            country=self.protonvpn.country.get_country_name(
                server.exit_country
            ),
            city=server.city,
            servername=server.name,
            protocol=protocol.upper()
        )

        self.state.on_next(result)

        # step 2
        connect_response = self.protonvpn.connect()

        logger.info("Dbus response: {}".format(connect_response))

        response = connect_response[
            DbusMonitorResponseEnum.RESPONSE
        ]
        state = response[DbusMonitorResponseEnum.STATE]

        # step 3
        if state == DbusVPNConnectionStateEnum.IS_ACTIVE:
            result = self.get_connected_state()
        else:
            result = ConnectError(
                self._conn_reason_msg[response[DbusMonitorResponseEnum.REASON]]
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
            self.protonvpn.disconnect()
        except exceptions.ConnectionNotFound:
            pass

        self.state.on_next(result)
        return False

    def get_connected_state(self):
        """Get connected state.

        Returns:
            ConnectedToVPNInfo
        """
        connection_status = self.protonvpn.get_connection_status()
        server = connection_status[
            ConnectionStatusEnum.SERVER_INFORMATION
        ]

        countries = [server.exit_country]
        if FeatureEnum.SECURE_CORE in [FeatureEnum(server.features)]:
            countries.append(server.ENTRY_COUNTRY)

        result = ConnectedToVPNInfo(
            protocol=connection_status[ConnectionStatusEnum.PROTOCOL],
            servername=server.name,
            countries=countries,
            city=server.city,
            ip=connection_status[ConnectionStatusEnum.SERVER_IP],
            load=str(int(server.load)),
            entry_country_code=server.entry_country,
            exit_country_code=server.exit_country
        )

        return result

    def get_not_connected_state(self):
        """Get not connected state.

        Returns:
            ConnectedToVPNInfo
        """
        location = self.utils.get_ip()
        result = NotConnectedToVPNInfo(
            ip=location.IP,
            isp=location.ISP,
            country=location.COUNTRY_CODE
        )

        return result

    def on_monitor_vpn(self):
        """Start VPN connection monitor.

        Since the VPN can be enabled via CLI,
        it should constantly monitor for an active
        protonvpn connection created by the library.

        The main method is started within a background process
        so that the UI will not freeze.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        process = self.bg_process.setup_no_params(self.on_startup_sync)
        process.start()
        return True

    def on_monitor_vpn_sync(self):
        """Monitor VPN connection.

        This methods monitors a VPN connection state from withing
        a thread. It is mainly used to track when a VPN connection
        is stopped and/or removed.
        """
        protonvpn_connection = self.protonvpn\
            .get_active_protonvpn_connection()
        if not protonvpn_connection:
            result = self.get_not_connected_state()

            self.state.on_next(result)

    def on_update_server_load(self):
        """Update server Load.

        The main method is started within a background process
        so that the UI will not freeze.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        process = self.bg_process.setup_no_params(
            self.on_update_server_load_sync
        )
        process.start()
        return True

    def on_update_server_load_sync(self):
        """Update server load.

        This metho actually refresh server cache. The library
        will automatically decide what it should cache, so this
        method can be safely used at anytime.

        This method is and should be executed within a python thread.
        """
        try:
            self.protonvpn.session.refresh_servers()
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
        process = self.bg_process.setup_no_params(
            self.on_update_speed_sync
        )
        process.start()
        return True

    def on_update_speed_sync(self):
        """Updates UI with current network speed.

        This method is and should be executed within a python thread,
        so that it does not freeze the UI due to the constant
        UI updates.
        """
        speed_result = self.utils.get_network_speed()
        up, dl = "-", "-"
        if len(speed_result) == 2:
            up, dl = str(speed_result[0]), str(speed_result[1])
        result = NetworkSpeed(
            download=dl,
            upload=up
        )

        self.state.on_next(result)
