from ...patterns.factory import WidgetFactory
from .country_row import CountryRow
from .country_header import CountryHeader
from .server_list_view_type import ServerListViewType


class NoneSecureCoreListView(ServerListViewType):

    def __init__(self, dashboard_view, server_list):
        super().__init__(dashboard_view, server_list)

    @property
    def widget(self):
        return self.__grid.widget

    def generate(self):
        self.__grid = WidgetFactory.grid("dummy")
        self.__grid.show = True

        country_header = CountryHeader(self.dv.application)
        row_counter = 0
        for country_item in self.yield_countries():
            if len(country_item) < 1:
                continue

            add_header = False
            header = country_header.create(
                country_item,
                self.server_list
            )
            if header:
                add_header = True
                self.__grid.attach(
                    header.widget, col=0,
                    row=row_counter + 1, width=1, height=1
                )
                self.header_tracker.append(header)

            country_grid_row = CountryRow(country_item, self.dv)
            row_counter += 1 + (1 if add_header else 0)

            self.__grid.attach(
                country_grid_row.event_box, col=0,
                row=row_counter, width=1, height=1
            )
            self.widget_position_tracker[
                country_item.country_name
            ] = country_grid_row

        self.country_rows = self.server_list.total_countries_count
