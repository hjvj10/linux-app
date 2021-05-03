from ...factory import WidgetFactory
from .server_row import ServerRow
from .server_header import ServerHeader


class ServerListRevealer:
    def __init__(self, dasbhoard_view, country_item, display_sc):
        self.dv = dasbhoard_view
        self.revealer = WidgetFactory.revealer("server_list")
        self.revealer_child_grid = WidgetFactory.grid("revealer_child")
        self.revealer_child_grid.add_class("server-names-grid")
        server_header = ServerHeader(self.dv.application)

        row_counter = 0
        for server in country_item.servers:

            add_header = False
            header = server_header.create(server, country_item)
            if header and not display_sc:
                add_header = True
                self.revealer_child_grid.attach(
                    header.widget, col=0,
                    row=row_counter + 1, width=1, height=1
                )

            row_counter += 1 + (1 if add_header else 0)

            self.revealer_child_grid.attach(
                ServerRow(self.dv, server, display_sc).event_box,
                row=row_counter
            )

        self.revealer.add(self.revealer_child_grid.widget)
