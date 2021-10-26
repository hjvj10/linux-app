
from gi.repository import GLib
from ..view_model.dataclass.dashboard import ServerListData, SwitchServerList
from .server_list_components.non_secure_core_server_list_view import NoneSecureCoreListView
from .server_list_components.secure_core_server_list_view import SecureCoreListView
from ..patterns.factory import BackgroundProcess
import concurrent.futures


class ServerListView():
    """ServerList class.

    Setup the server list.
    """
    def __init__(self, dashboard_view):
        self.dv = dashboard_view
        self.dashboard_view_model = self.dv.dashboard_view_model
        self.dashboard_view_model.state.subscribe(
            lambda state: GLib.idle_add(self.render_view_state, state)
        )
        self.__display_secure_core_list = False
        self.__secure_core_view = SecureCoreListView()
        self.__none_secure_core_view = NoneSecureCoreListView()
        self.counter = 0

    def render_view_state(self, state):
        if isinstance(state, ServerListData):
            self.__display_secure_core_list = True if state.display_secure_core else False
            self._populate_async(
                state.server_list,
                self.dashboard_view_model.on_startup_load_dashboard_resources_async
            )
        if isinstance(state, SwitchServerList):
            self.__display_secure_core_list = True if state.display_secure_core else False
            self._switch_server_list_view_async()

    def _populate_async(self, server_list, callback):
        self.__server_list = server_list
        process = BackgroundProcess.factory("gtask")
        process.setup(target=self.__populate, callback=callback)
        process.start()

    def __populate(self, *_):
        _jobs = [
            [self.__secure_core_view, self.__server_list.secure_core, self.dv],
            [self.__none_secure_core_view, self.__server_list.none_secure_core, self.dv],
        ]

        with concurrent.futures.ThreadPoolExecutor() as exec:
            exec.map(self._generate_process, _jobs)

        GLib.idle_add(self.__attach_server_list)

    def _generate_process(self, data):
        instance = data[0]
        servers = data[1]
        dashboard_view = data[2]

        instance.generate(dashboard_view, servers)

    def _switch_server_list_view_async(self, callback=None):
        process = BackgroundProcess.factory("gtask")
        process.setup(target=self.__switch_server_list_view, callback=callback)
        process.start()

    def __switch_server_list_view(self, *_):
        GLib.idle_add(self.__attach_server_list)

    def __attach_server_list(self):
        existing_child = self.dv.server_list_grid.get_child_at(0, 0)
        if existing_child:
            self.dv.server_list_grid.remove_row(0)

        widget = self.__none_secure_core_view.widget
        if self.__display_secure_core_list:
            widget = self.__secure_core_view.widget

        try:
            self.dv.server_list_grid.attach(
                widget, 0, 0, 1, 1
            )
        except Exception as e:
            print(e)

        return False

    def filter_server_list(self, user_input):
        if self.__display_secure_core_list:
            self.__secure_core_view.filter_server_list(user_input)
        else:
            self.__none_secure_core_view.filter_server_list(user_input)
