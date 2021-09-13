from abc import abstractmethod

class ServerListViewType:

    def __init__(self, dashboard_view, server_list):
        self.dv = dashboard_view
        self.header_tracker = []
        self.country_rows = 0
        self.server_list = server_list
        self.widget_position_tracker = {}

    @property
    @abstractmethod
    def widget():
        pass

    @abstractmethod
    def generate():
        pass

    def yield_countries(self):
        for country_item in self.server_list.servers:
            yield country_item

    def filter_server_list(self, user_input):
        """Filter server list based on user input.

        Args:
            user_input (string): what to search for

        It either hides or shows the grid/row for a specific country.

        06/2021: Search is only possible for country names
        """
        filtered_country_widgets = [
            country_row
            for country_name, country_row
            in self.widget_position_tracker.items()
            if user_input.lower() in country_name.lower()
        ]

        try:
            self.__show_headers(False)
        except: # noqa
            pass
        else:
            if len(user_input) < 1:
                self.__show_headers(True)

        for _, country_row in self.widget_position_tracker.items():
            if country_row in filtered_country_widgets:
                country_row.row_grid.show = True
                continue

            country_row.row_grid.show = False

    def __show_headers(self, bool_val):
        """Sets header visibility.

        Ideally the headers should be hidden when a user is performing a search,
        otherwise they should be displayed.
        """
        for header in self.header_tracker:
            header.show = bool_val
