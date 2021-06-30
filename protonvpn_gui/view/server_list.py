from ..patterns.factory import WidgetFactory
from .server_list_components.country_header import CountryHeader
from .server_list_components.country_row import CountryRow

from gi.repository import GLib
from ..view_model.dashboard import ServerListData
from ..model.background_process import BackgroundProcess


class ServerListView():
    """ServerList class.

    Setup the server list.
    """
    def __init__(self, dashboard_view, dashboard_view_model):
        self.__country_rows = 0
        self.dv = dashboard_view
        self.dashboard_view_model = dashboard_view_model
        self.dashboard_view_model.state.subscribe(
            lambda state: GLib.idle_add(self.render_view_state, state)
        )
        self.__server_list = None
        self.__country_widget_position_tracker = {}
        self.__header_tracker = []

    def render_view_state(self, state):
        if isinstance(state, ServerListData):
            self._populate_async(
                state.server_list,
                self.dv.dashboard_view_model.on_startup_load_dashboard_resources_async
            )

    @property
    def total_of_existing_countries(self):
        return self.__country_rows

    def _populate_async(self, server_list, callback):
        self.__server_list = server_list
        process = BackgroundProcess.get("gtask")
        process.setup(callback=callback)
        process.start(self.__populate)

    def __populate(self, *_):
        server_list_widget = self.__generate_widget_list().widget
        GLib.idle_add(self.__attach_server_list, server_list_widget)

    def __attach_server_list(self, widget):
        if self.dv.server_list_grid.get_child_at(0, 0):
            self.dv.server_list_grid.remove_row(0)
        self.dv.server_list_grid.attach(
            widget, 0, 0, 1, 1
        )
        return False

    def __generate_widget_list(self):
        replaceable_child_grid = WidgetFactory.grid("dummy")
        replaceable_child_grid.show = True

        country_header = CountryHeader(self.dv.application)
        row_counter = 0
        for country_item in self._yield_countries():
            if len(country_item) < 1:
                continue

            add_header = False
            header = country_header.create(
                country_item,
                self.__server_list
            )
            if header and not self.__server_list.display_secure_core:
                add_header = True
                replaceable_child_grid.attach(
                    header.widget, col=0,
                    row=row_counter + 1, width=1, height=1
                )
                self.__header_tracker.append(header)

            country_grid_row = CountryRow(
                country_item, self.dv,
                display_sc=self.__server_list.display_secure_core
            )
            row_counter += 1 + (1 if add_header else 0)

            replaceable_child_grid.attach(
                country_grid_row.event_box, col=0,
                row=row_counter, width=1, height=1
            )
            self.__country_widget_position_tracker[
                country_item.country_name
            ] = country_grid_row

        self.__country_rows = self.__server_list.total_countries_count
        return replaceable_child_grid

    def _yield_countries(self):
        for country_item in self.__server_list.servers:
            yield country_item

    def filter_server_list(self, user_input):
        filtered_country_widgets = [
            country_row
            for country_name, country_row
            in self.__country_widget_position_tracker.items()
            if user_input.lower() in country_name.lower()
        ]

        self.__show_headers(False)
        if len(user_input) < 1:
            self.__show_headers(True)

        for _, country_row in self.__country_widget_position_tracker.items():
            if country_row in filtered_country_widgets:
                country_row.row_grid.show = True
                continue

            country_row.row_grid.show = False

    def __show_headers(self, bool_val):
        """Sets header visibility.

        Ideally the headers should be hidden when a user is performing a search,
        otherwise they should be displayed.
        """
        for header in self.__header_tracker:
            header.show = bool_val
