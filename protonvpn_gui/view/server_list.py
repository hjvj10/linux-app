
from gi.repository import GLib
from ..view_model.dashboard import ServerListData,SwitchServerList
from .server_list_components.non_secure_core_server_list_view import NoneSecureCoreListView
from .server_list_components.secure_core_server_list_view import SecureCoreListView
from ..patterns.factory import BackgroundProcess
from ..enums import GTKPriorityEnum


class ServerListView():
    """ServerList class.

    Setup the server list.
    """
    def __init__(self, dashboard_view, dashboard_view_model):
        self.dv = dashboard_view
        self.dashboard_view_model = dashboard_view_model
        self.dashboard_view_model.state.subscribe(
            lambda state: GLib.idle_add(self.render_view_state, state)
        )
        self.__display_secure_core_list = False
        self.__secure_core_view = None
        self.__none_secure_core_view = None

    def render_view_state(self, state):
        if isinstance(state, ServerListData):
            self._populate_async(
                state.server_list,
                self.dv.dashboard_view_model.on_startup_load_dashboard_resources_async
            )
            self.__display_secure_core_list = True if state.display_secure_core else False
        if isinstance(state, SwitchServerList):
            self.__display_secure_core_list = True if state.display_secure_core else False
            self._switch_server_list_view_async()

    def _populate_async(self, server_list, callback):
        self.__server_list = server_list
        process = BackgroundProcess.factory("gtask")
        process.setup(target=self.__populate, callback=callback)
        process.start()

    def __populate(self, *_):
        self.__secure_core_view = SecureCoreListView(self.dv, self.__server_list.secure_core)
        self.__none_secure_core_view = NoneSecureCoreListView(self.dv, self.__server_list.none_secure_core)

        self.__secure_core_view.generate()
        self.__none_secure_core_view.generate()

        GLib.main_context_default().invoke_full(GTKPriorityEnum.PRIORITY_HIGH.value, self.__attach_server_list)

    def _switch_server_list_view_async(self, callback=None):
        process = BackgroundProcess.factory("gtask")
        process.setup(target=self.__switch_server_list_view, callback=callback)
        process.start()

    def __switch_server_list_view(self, *_):
        GLib.main_context_default().invoke_full(GTKPriorityEnum.PRIORITY_HIGH.value, self.__attach_server_list)

    def __attach_server_list(self):
        if self.dv.server_list_grid.get_child_at(0, 0):
            self.dv.server_list_grid.remove_row(0)

        widget = self.__none_secure_core_view.widget
        if self.__display_secure_core_list:
            widget = self.__secure_core_view.widget

        self.dv.server_list_grid.attach(
            widget, 0, 0, 1, 1
        )
        return False

    def filter_server_list(self, user_input):
        if self.__display_secure_core_list:
            self.__secure_core_view.filter_server_list(user_input)
        else:
            self.__none_secure_core_view.filter_server_list(user_input)

