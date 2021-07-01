from dataclasses import dataclass

from protonvpn_nm_lib import exceptions
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.enums import (ConnectionMetadataEnum,
                                    ConnectionStartStatusEnum,
                                    ConnectionStatusEnum, ConnectionTypeEnum,
                                    FeatureEnum, KillswitchStatusEnum,
                                    NetshieldTranslationEnum,
                                    SecureCoreStatusEnum, ServerTierEnum,
                                    VPNConnectionReasonEnum,
                                    VPNConnectionStateEnum)

from ..enums import (DashboardKillSwitchIconEnum, DashboardNetshieldIconEnum,
                     DashboardSecureCoreIconEnum)
from ..logger import logger
from ..rx.subject.replaysubject import ReplaySubject
from ..patterns.factory import BackgroundProcess


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


@dataclass
class QuickSettingsStatus:
    secure_core: DashboardSecureCoreIconEnum
    netshield: DashboardNetshieldIconEnum
    killswitch: DashboardKillSwitchIconEnum


@dataclass
class DisplayDialog:
    title: str
    text: str


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
        VPNConnectionStateEnum.UNKNOWN: "State of "
        "VPN connection is unkown.",
        VPNConnectionStateEnum.NEEDS_CREDENTIALS: "The VPN "
        "connection is missing credentials.",
        VPNConnectionStateEnum.FAILED: "Failed to "
        "connect to VPN.",
        VPNConnectionStateEnum.DISCONNECTED: "VPN connection "
        "has been disconnected.",
        VPNConnectionStateEnum.UNKNOWN_ERROR: "Unknown error."
    }

    _conn_reason_msg = {
        VPNConnectionReasonEnum.UNKNOWN: "The reason for the active "
        "connection state change is unknown.",
        VPNConnectionReasonEnum.NOT_PROVIDED: "No reason was given "
        "for the active connection state change.",
        VPNConnectionReasonEnum.USER_HAS_DISCONNECTED: "The active "
        "connection changed state because the user "
        "disconnected it.",
        VPNConnectionReasonEnum.DEVICE_WAS_DISCONNECTED: "The active "
        "connection changed state because the device it was using "
        "was disconnected.",
        VPNConnectionReasonEnum.SERVICE_PROVIDER_WAS_STOPPED: "The "
        "service providing the VPN connection was stopped.",
        VPNConnectionReasonEnum.IP_CONFIG_WAS_INVALID: "The IP "
        "configuration of the active connection is invalid.",
        VPNConnectionReasonEnum.CONN_ATTEMPT_TO_SERVICE_TIMED_OUT: "The "
        "connection attempt to the VPN service timed out.",
        VPNConnectionReasonEnum.TIMEOUT_WHILE_STARTING_VPN_SERVICE_PROVIDER: # noqa
        "A timeout occurred while starting the service providing "
        "the VPN connection.",
        VPNConnectionReasonEnum.START_SERVICE_VPN_CONN_SERVICE_FAILED:
        "Starting the service providing the VPN connection failed.",
        VPNConnectionReasonEnum.SECRETS_WERE_NOT_PROVIDED: "Necessary "
        "secrets for the connection were not provided.",
        VPNConnectionReasonEnum.SERVER_AUTH_FAILED: "Authentication "
        "to the server failed.",
        VPNConnectionReasonEnum.DELETED_FROM_SETTINGS: "The connection "
        "was deleted from settings.",
        VPNConnectionReasonEnum.MASTER_CONN_FAILED_TO_ACTIVATE: "Master "
        "connection failed to activate.",
        VPNConnectionReasonEnum.CREATE_SOFTWARE_DEVICE_LINK_FAILED:
        "Could not create the software device link.",
        VPNConnectionReasonEnum.VPN_DEVICE_DISAPPEARED: "The device this "
        "connection depended on disappeared.",
        VPNConnectionReasonEnum.UNKNOWN_ERROR: "Unknown reason occured."
    }

    def __init__(self, utils, server_list):
        self.utils = utils
        self.__quick_settings_vm = QuickSettingsViewModel(self)
        self.__server_list_vm = ServerListViewModel(self, server_list)
        self.state = ReplaySubject(buffer_size=1)

    @property
    def quick_settings_view_model(self):
        return self.__quick_settings_vm

    @property
    def server_list_view_model(self):
        return self.__server_list_vm

    def on_switch_secure_core_button(self, *args):
        self.__quick_settings_vm.on_switch_secure_core_button(*args)

    def on_switch_netshield_button(self, *args):
        self.__quick_settings_vm.on_switch_netshield_button(*args)

    def on_switch_killswitch_button(self, *args):
        self.__quick_settings_vm.on_switch_killswitch_button(*args)

    def on_update_server_load(self):
        self.__server_list_vm.on_update_server_load_async()

    def on_startup_preload_resources_async(self):
        """Async load initial UI components such as quick settings and
        server list."""
        self.state.on_next(Loading())
        process = BackgroundProcess.factory()
        process.setup(self.__on_startup)
        process.start()

    def __on_startup(self):
        """Load initial UI components such as quick settings and
        server list.

        This needs to be pre-loaded before displaying the dashboard."""
        self.state.on_next(self.get_quick_settings_state())
        try:
            self.__server_list_vm.on_load_servers()
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = DisplayDialog(
                title="Error Loading Servers",
                text=str(e)
            )
            self.state.on_next(result)

    def on_startup_load_dashboard_resources_async(self, *_):
        """Async load dashboard resources."""
        process = BackgroundProcess.factory()
        process.setup(self.__on_startup_load_dashboard_resources)
        process.start()

    def __on_startup_load_dashboard_resources(self):
        """Load dashboard resources.

        This updates the rest of dashboard UI components.
        """
        try:
            protonvpn.ensure_connectivity()
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = NotConnectedToVPNInfo(
                ip=None,
                isp=None,
                country=None,
                perma_ks_enabled=protonvpn.get_settings().killswitch == KillswitchStatusEnum.HARD
            )
        else:
            try:
                if not protonvpn.get_active_protonvpn_connection():
                    result = self.__get_not_connected_state()
                else:
                    result = self.__get_connected_state()
            except (exceptions.ProtonVPNException, Exception) as e:
                logger.exception(e)
                result = DisplayDialog(
                    title="Error Getting VPN State",
                    text=str(e)
                )

        self.state.on_next(result)

    def on_quick_connect(self):
        """Quick connect to ProtonVPN.

        This method sets the state of the UIsync_async
        to preparing and calls the method
        connect() with ConnectionTypeEnum type.

        Ideally the on_quick_connect() method should be run
        within a python thread. Due to current situation, it is
        not done so due the reasons specified in class docstring.
        """
        logger.info("Preparing to quick connect")
        self.connect(ConnectionTypeEnum.FASTEST)

    def on_country_connect(self, country_code):
        """Connect to a specific country.

        This method sets the state of the UI
        to preparing and calls the method
        connect() with ConnectionTypeEnum type.

        Ideally this method should be run
        as a background process.
        """
        logger.info("Preparing to connect to country \"{}\"".format(
            country_code
        ))
        self.connect(
            ConnectionTypeEnum.COUNTRY,
            country_code
        )

    def on_servername_connect(self, servername):
        """Connect to a specific server.

        This method sets the state of the UI
        to preparing and calls the method
        connect() with ConnectionTypeEnum type.

        Ideally this method should be run
        as a background process.
        """
        logger.info("Preparing to connect to servername \"{}\"".format(
            servername
        ))
        self.connect(
            ConnectionTypeEnum.SERVERNAME,
            servername
        )

    def on_reconnect(self):
        """Reconnect to previously connected server.

        This method sets the state of the UI
        to preparing and calls the method
        connect() with ConnectionTypeEnum type.

        Ideally this method should be run
        as a background process.
        """
        logger.info("Preparing to reconnect")
        self.connect(connection_type_enum=None, reconnect=True)

    def connect(self, connection_type_enum, extra_arg=None, reconnect=False):
        """General connect method.

        This method should always be used when connecting to
        VPN. Ideally should be run within a python thread.

        It initially attemps to setup the connection, then updated
        the UI accordingly and only the proceeds to connect to the VPN.
        This is done so that the user is aware of where the connections
        is made to during the ConnectInProgressInfo() state.

        Args:
            connection_type_enum (ConnectionTypeEnum)
            extra_arg: (optional)
                this argument is only set if the user is
                connecting with ConnectionTypeEnum.COUNTRY
                or ConnectionTypeEnum.SERVERNAME.
        """
        logger.info("Setting up connection")
        result = ConnectPreparingInfo()
        self.state.on_next(result)
        setup_connection_error = False
        try:
            if reconnect:
                server = protonvpn.setup_reconnect()
            else:
                server = protonvpn.setup_connection(
                    connection_type=connection_type_enum,
                    connection_type_extra_arg=extra_arg
                )
        except exceptions.ServerCacheNotFound as e:
            logger.exception(e)
            setup_connection_error = \
                "\nServer cache is missing. " \
                "Please ensure that you have internet connection to " \
                "cache servers."
        except exceptions.ServernameServerNotFound as e:
            logger.exception(e)
            setup_connection_error = \
                "\nNo server could be found with the provided servername.\n" \
                "Either the server is under maintenance or\nyou " \
                "don't have access to it with your plan."
        except exceptions.FeatureServerNotFound as e:
            logger.exception(e)
            setup_connection_error = \
                "\nNo servers were found with the provided feature.\n" \
                "Either the servers with the provided feature are " \
                "under maintenance or\nyou don't have access to the " \
                "specified feature with your plan."
        except exceptions.FastestServerInCountryNotFound as e:
            logger.exception(e)
            setup_connection_error = \
                "\nNo server could be found with the provided country.\n" \
                "Either the provided country is not available or\n" \
                "you don't have access to the specified country " \
                "with your plan."
        except (
            exceptions.RandomServerNotFound, exceptions.FastestServerNotFound
        ) as e:
            logger.exception(e)
            setup_connection_error = \
                "\nNo server could be found.\n" \
                "Please ensure that you have an active internet connection.\n" \
                "If the issue persists, please contact support."
        except exceptions.DefaultOVPNPortsNotFoundError as e:
            logger.exception(e)
            setup_connection_error = \
                "\nThere are missing configurations. " \
                "Please ensure that you have internet connection."
        except exceptions.IllegalServername as e:
            logger.exception(e)
            setup_connection_error = \
                "\nProvided servername is invalid. Please ensure that you've " \
                "correctly typed the servername."
        except exceptions.DisableConnectivityCheckError as e:
            logger.exception(e)
            setup_connection_error = \
                "\nIt was not possible to automatically disable connectivity check. " \
                "This step is necessary for the Kill Switch to function properly, " \
                "please disable connectivity check copying and pasting the following" \
                "command into terminal:\nbusctl set-property org.freedesktop.NetworkManager " \
                "/org/freedesktop/NetworkManager org.freedesktop.NetworkManager " \
                "ConnectivityCheckEnabled 'b' 0"
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            setup_connection_error = \
                "\nAn unknown error has occured. Please ensure that you have " \
                "internet connectivity." \
                "\nIf the issue persists, please contact support."

        if setup_connection_error:
            result = ConnectError(
                setup_connection_error
            )
            self.state.on_next(result)
            return

        logger.info("Connection was setup")
        # step 1
        self.__display_connection_information_during_connect(server)

        # step 2
        logger.info("Attempting to connect")
        connect_response = protonvpn.connect()
        logger.info("Dbus response: {}".format(connect_response))
        state = connect_response[ConnectionStartStatusEnum.STATE]

        # step 3
        try:
            if state == VPNConnectionStateEnum.IS_ACTIVE:
                result = self.__get_connected_state()
            else:
                result = ConnectError(
                    self._conn_reason_msg[
                        connect_response[ConnectionStartStatusEnum.REASON]
                    ]
                )
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = DisplayDialog(
                title="Unable to get Connection Data",
                text=str(e)
            )

        self.state.on_next(self.get_quick_settings_state())
        self.state.on_next(result)

    def __display_connection_information_during_connect(self, server):
        connection_metadata = protonvpn.get_connection_metadata()
        protocol = connection_metadata[ConnectionMetadataEnum.PROTOCOL.value]
        result = ConnectInProgressInfo(
            entry_country=protonvpn.get_country().get_country_name(
                server.entry_country
            ),
            exit_country=protonvpn.get_country().get_country_name(
                server.exit_country
            ),
            city=server.city,
            servername=server.name,
            protocol=protocol.upper(),
            is_secure_core=FeatureEnum.SECURE_CORE in server.features
        )

        logger.info("Displaying connection information")
        self.state.on_next(result)

    def on_disconnect(self):
        """On disconnect method.

        Ideally the on_disconnect() method should be run
        within a python thread, but is not done so due to
        the reasons specified in class docstring.
        """
        result = self.__get_not_connected_state()
        try:
            protonvpn.disconnect()
        except (exceptions.ConnectionNotFound, AttributeError):
            pass

        self.state.on_next(result)
        return False

    def __get_connected_state(self):
        """Get connected state.

        Returns:
            ConnectedToVPNInfo
        """
        connection_status = protonvpn.get_connection_status()
        server = connection_status[
            ConnectionStatusEnum.SERVER_INFORMATION
        ]
        countries = [server.exit_country]
        if FeatureEnum.SECURE_CORE in server.features:
            countries.append(server.entry_country)

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

    def __get_not_connected_state(self):
        """Get not connected state.

        Returns:
            ConnectedToVPNInfo
        """
        location = self.utils.get_ip()
        result = NotConnectedToVPNInfo(
            ip=location.IP,
            isp=location.ISP,
            country=location.COUNTRY_CODE,
            perma_ks_enabled=protonvpn.get_settings().killswitch == KillswitchStatusEnum.HARD
        )

        return result

    def get_quick_settings_state(self):
        settings = protonvpn.get_settings()
        ks_quick_setting = {
            KillswitchStatusEnum.DISABLED: DashboardKillSwitchIconEnum.OFF,
            KillswitchStatusEnum.SOFT: DashboardKillSwitchIconEnum.ON_ACTIVE,
            KillswitchStatusEnum.HARD:
            DashboardKillSwitchIconEnum.ALWAYS_ON_ACTIVE
        }
        ns_quick_setting = {
            NetshieldTranslationEnum.DISABLED: DashboardNetshieldIconEnum.OFF,
            NetshieldTranslationEnum.MALWARE:
            DashboardNetshieldIconEnum.MALWARE_ACTIVE,
            NetshieldTranslationEnum.ADS_MALWARE:
            DashboardNetshieldIconEnum.MALWARE_ADS_ACTIVE
        }
        sc_quick_setting = {
            SecureCoreStatusEnum.OFF: DashboardSecureCoreIconEnum.OFF,
            SecureCoreStatusEnum.ON: DashboardSecureCoreIconEnum.ON_ACTIVE
        }

        state = QuickSettingsStatus(
            secure_core=sc_quick_setting[settings.secure_core],
            netshield=ns_quick_setting[settings.netshield],
            killswitch=ks_quick_setting[settings.killswitch],
        )

        return state

    def on_monitor_vpn_async(self):
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
        process = BackgroundProcess.factory()
        process.setup(self.__on_monitor_vpn)
        process.start()
        return True

    def __on_monitor_vpn(self):
        """Monitor VPN connection.

        This methods monitors a VPN connection state from withing
        a thread. It is mainly used to track when a VPN connection
        is stopped and/or removed.
        """
        protonvpn_connection = protonvpn\
            .get_active_protonvpn_connection()

        try:
            if not protonvpn_connection:
                result = self.__get_not_connected_state()
            else:
                result = self.__get_connected_state()
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = DisplayDialog(
                title="Unable to get Connection Data",
                text=str(e)
            )

        self.state.on_next(result)

    def on_update_speed_async(self):
        """Update network speed.

        The main method is started within a python thread
        so that the UI does not freeze up.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        process = BackgroundProcess.factory()
        process.setup(
            self.__on_update_speed
        )
        process.start()
        return True

    def __on_update_speed(self):
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


class ServerListViewModel:
    def __init__(self, dashboard_view_model, server_list):
        self.dashboard_vm = dashboard_view_model
        self.server_list = server_list

    def on_load_servers_async(self):
        process = BackgroundProcess.factory()
        process.setup(
            self.on_load_servers
        )
        process.start()

    def on_load_servers(self):
        if not self.server_list.servers:
            self.__generate_server_list()

        self.server_list.display_secure_core = \
            protonvpn.get_settings().secure_core == SecureCoreStatusEnum.ON

        state = ServerListData(self.server_list)
        self.dashboard_vm.state.on_next(state)

    def __generate_server_list(self):
        self.server_list.generate_list(
            ServerTierEnum(protonvpn.get_session().vpn_tier)
        )

    def on_update_server_load_async(self):
        """Update server Load.

        The main method is started within a background process
        so that the UI will not freeze.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        process = BackgroundProcess.factory()
        process.setup(
            self.__on_update_server_load
        )
        process.start()

    def __on_update_server_load(self):
        """Update server load.

        This method refreshes server cache. The library
        will automatically decide what it should cache, so this
        method can be safely used at anytime.

        This method is and should be executed within a python thread.
        """
        session = protonvpn.get_session()
        try:
            session.servers
        except Exception as e:
            logger.exception(e)

        result = self.dashboard_vm.__get_connected_state()

        self.dashboard_vm.state.on_next(result)


class QuickSettingsViewModel:

    def __init__(self, dashboard_view_model):
        self.dashboard_vm = dashboard_view_model

    def on_switch_secure_core_button(self, secure_core_enum):
        """On reconnect Secure Core."""
        logger.info("Setting secure core to \"{}\"".format(secure_core_enum))
        protonvpn.get_settings().secure_core = secure_core_enum

        self.dashboard_vm.server_list_view_model.on_load_servers_async()

        if protonvpn.get_active_protonvpn_connection():
            logger.info("Preparing reconnect with \"{}\"".format(
                secure_core_enum
            ))
            self.__prepare_secure_core_reconnect(secure_core_enum)
        else:
            self.dashboard_vm.state.on_next(self.dashboard_vm.get_quick_settings_state())

    def __prepare_secure_core_reconnect(self, secure_core_enum):
        """Prepares Secure Core reconnect.

        Args:
            secure_core_enum (SecureCoreStatusEnum)

        If there is an active connection, this method will attempt
        to reconnect to a server which the exit country matches
        the entry country of a secure core server. If none is found,
        then it will only call get_fastest_server(), since the library
        is aware of this status.
        """
        connection_metadata = protonvpn.get_connection_metadata()
        connected_server = connection_metadata[
            ConnectionMetadataEnum.SERVER.value
        ]
        exit_country = protonvpn.config_for_server_with_servername(
            connected_server
        ).exit_country

        server = None
        if secure_core_enum == SecureCoreStatusEnum.ON:
            self.dashboard_vm.server_list_view_model.server_list.display_secure_core = True
            servers_list = list(map(
                lambda country: list(filter(
                    lambda server:
                    server.exit_country_code.lower() == exit_country.lower(),
                    country.servers
                )),
                self.dashboard_vm.server_list_view_model.server_list.servers
            ))
            flattened_servers = [
                server for sub in servers_list for server in sub
            ]
            if len(flattened_servers) > 0:
                flattened_servers.sort(
                    key=lambda server: server.score, reverse=True
                )
                server = flattened_servers[0]

        if not server:
            server = protonvpn.config_for_fastest_server()

        logger.info("Preparing to connect to servername \"{}\"".format(
            server.name
        ))
        self.dashboard_vm.connect(
            ConnectionTypeEnum.SERVERNAME,
            server.name
        )

    def on_switch_netshield_button(self, netshield_enum):
        logger.info("Setting netshield to \"{}\"".format(netshield_enum))
        protonvpn.get_settings().netshield = netshield_enum
        if protonvpn.get_active_protonvpn_connection():
            logger.info("Preparing reconnect with \"{}\"".format(
                netshield_enum
            ))
            self.dashboard_vm.on_reconnect()
        else:
            self.dashboard_vm.state.on_next(self.dashboard_vm.get_quick_settings_state())

    def on_switch_killswitch_button(self, ks_enum):
        logger.info("Setting killswitch to \"{}\"".format(ks_enum))
        protonvpn.get_settings().killswitch = ks_enum
        active_connection = protonvpn.get_active_protonvpn_connection()
        if active_connection and ks_enum == KillswitchStatusEnum.SOFT:
            logger.info("Preparing reconnect with \"{}\"".format(
                ks_enum
            ))
            self.dashboard_vm.on_reconnect()
        else:
            self.dashboard_vm.state.on_next(self.dashboard_vm.get_quick_settings_state())
