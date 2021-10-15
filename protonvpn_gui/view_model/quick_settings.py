from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.enums import (ConnectionMetadataEnum, ConnectionTypeEnum,
                                    KillswitchStatusEnum, SecureCoreStatusEnum)

from ..logger import logger


class QuickSettingsViewModel:

    def __init__(self):
        self.dashboard_vm = None

    @property
    def dashboard_view_model(self):
        return self.dashboard_vm

    @dashboard_view_model.setter
    def dashboard_view_model(self, newvalue):
        self.dashboard_vm = newvalue

    def on_switch_secure_core_button(self, secure_core_enum):
        """On reconnect Secure Core."""
        logger.info("Setting secure core to \"{}\"".format(secure_core_enum))
        protonvpn.get_settings().secure_core = secure_core_enum

        self.dashboard_vm.server_list_view_model.on_switch_server_list_view_async()

        self.dashboard_vm.state.on_next(self.dashboard_vm.get_quick_settings_state())

        if protonvpn.get_active_protonvpn_connection():
            logger.info("Preparing reconnect with \"{}\"".format(
                secure_core_enum
            ))
            self.__prepare_secure_core_reconnect(secure_core_enum)

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
            servers_list = list(map(
                lambda country: list(filter(
                    lambda server:
                    server.exit_country_code.lower() == exit_country.lower(),
                    country.servers
                )),
                self.dashboard_vm.server_list_view_model.server_list.secure_core.servers
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
        self.dashboard_vm.state.on_next(self.dashboard_vm.get_quick_settings_state())

        if protonvpn.get_active_protonvpn_connection():
            logger.info("Preparing reconnect with \"{}\"".format(
                netshield_enum
            ))
            self.dashboard_vm.on_reconnect()

    def on_switch_killswitch_button(self, ks_enum):
        logger.info("Setting killswitch to \"{}\"".format(ks_enum))
        protonvpn.get_settings().killswitch = ks_enum
        active_connection = protonvpn.get_active_protonvpn_connection()
        self.dashboard_vm.state.on_next(self.dashboard_vm.get_quick_settings_state())

        if active_connection and ks_enum == KillswitchStatusEnum.SOFT:
            logger.info("Preparing reconnect with \"{}\"".format(
                ks_enum
            ))
            self.dashboard_vm.on_reconnect()
