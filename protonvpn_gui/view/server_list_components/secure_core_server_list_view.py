from ...patterns.factory import WidgetFactory
from .country_row import CountryRow
from .server_list_view_type import ServerListViewType


class SecureCoreListView(ServerListViewType):

    def __init__(self):
        self.__grid = None
        super().__init__()

    def generate(self, dashboard_view, server_list=None):
        if self.__grid:
            self.destroy_existing_widgets()

        if server_list:
            self.update_server_list(server_list)

        self.__generate(dashboard_view)

    @property
    def widget(self):
        return self.__grid.widget

    def __generate(self, dashboard_view):
        self.__grid = WidgetFactory.grid("dummy")
        self.__grid.show = True

        row_counter = 0
        for country_item in self.yield_countries():
            if len(country_item) < 1:
                continue

            country_grid_row = CountryRow(country_item, dashboard_view, True)
            row_counter += 1

            self.__grid.attach(
                country_grid_row.event_box, col=0,
                row=row_counter, width=1, height=1
            )
            self.widget_position_tracker[
                country_item.country_name
            ] = country_grid_row

        self.country_rows = self.server_list.total_countries_count

    def destroy_existing_widgets(self):
        for _, widget in self.widget_position_tracker.items():
            widget.__delete__()

        self.__grid = None
        self.server_list = None
        self.country_rows = None
        self.widget_position_tracker = None
        self.header_tracker = None
        self.widget_position_tracker = {}
        self.header_tracker = []
