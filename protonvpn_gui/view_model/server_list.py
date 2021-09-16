from ..patterns.factory import BackgroundProcess
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.enums import ServerTierEnum, SecureCoreStatusEnum
from ..enums import GTKPriorityEnum
from .dataclass.dashboard import ServerListData, SwitchServerList
from ..logger import logger


class ServerListViewModel:
    def __init__(self, dashboard_view_model, server_list):
        self.dashboard_vm = dashboard_view_model
        self.server_list = server_list
        self.__update_server_load = False

    def on_switch_server_list_view_async(self):
        process = BackgroundProcess.factory("gtask")
        process.setup(self.on_switch_server_list_view_sync)
        process.start()

    def on_switch_server_list_view_sync(self, *_):
        state = SwitchServerList(
            display_secure_core=protonvpn.get_settings().secure_core == SecureCoreStatusEnum.ON
        )
        self.dashboard_vm.main_context.invoke_full(
            GTKPriorityEnum.PRIORITY_DEFAULT.value, self.dashboard_vm.state.on_next, state
        )

    def on_load_servers_async(self, *_):
        process = BackgroundProcess.factory("gtask")
        process.setup(self.on_load_servers)
        process.start()

    def on_load_servers(self, *_):
        self.__generate_server_list()
        state = ServerListData(
            server_list=self.server_list,
            display_secure_core=protonvpn.get_settings().secure_core == SecureCoreStatusEnum.ON
        )
        self.dashboard_vm.main_context.invoke_full(
            GTKPriorityEnum.PRIORITY_DEFAULT.value, self.dashboard_vm.state.on_next, state
        )

    def __generate_server_list(self):
        self.server_list.generate_list(
            ServerTierEnum(protonvpn.get_session().vpn_tier)
        )

    def __finish_on_update_server_load(self, self_thread, task, data):
        var = bool(task.propagate_int())
        if var:
            self.__update_server_load = False

    def on_update_server_load_async(self):
        """Update server Load.

        The main method is started within a background process
        so that the UI will not freeze.

        Since it is being invoked via a GLib method, it returns True
        so that the method can be called again. If returned False,
        then the callback would stop.
        """
        if self.__update_server_load:
            return

        self.__update_server_load = True
        process = BackgroundProcess.factory("gtask")
        process.setup(
            self.__on_update_server_load,
            callback=self.__finish_on_update_server_load
        )
        process.start()

    def __on_update_server_load(self, task, self_thread, data, cancellable):
        """Update server load.

        This method refreshes server cache. The library
        will automatically decide what it should cache, so this
        method can be safely used at anytime.

        This method is and should be executed within a python thread.
        """
        session = protonvpn.get_session()

        # By requests the servers, it will automatically trigger a request
        # to the API, to updated the serverlist if needed.
        try:
            session.servers
        except Exception as e:
            # Display dialog with message
            logger.exception(e)
            task.return_int(0)
            return

        try:
            self.on_load_servers_async(False)
        except Exception as e:
            # Display dialog with message
            logger.exception(e)
            task.return_int(0)
        else:
            task.return_int(1)
