from ...factory import WidgetFactory
from .server_row import ServerRow


class ServerListRevealer:
    def __init__(self, dasbhoard_view, servers, display_sc):
        self.dv = dasbhoard_view
        self.revealer = WidgetFactory.revealer("server_list")
        self.revealer_child_grid = WidgetFactory.grid("revealer_child")

        self.__row_counter = 0
        for server in servers:
            self.revealer_child_grid.attach(
                ServerRow(self.dv, server, display_sc).event_box,
                row=self.__row_counter
            )
            self.__row_counter += 1

        self.revealer.add(self.revealer_child_grid.widget)
