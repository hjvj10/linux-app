from ...patterns.factory import WidgetFactory
from .server_row import ServerRow
from .server_header import ServerHeader
import weakref


class ServerListRevealer:
    def __init__(self, dasbhoard_view, country_item, display_sc):
        self.revealer = WidgetFactory.revealer("server_list")

        _revealer_child_grid = WidgetFactory.grid("revealer_child")
        revealer_child_grid = weakref.proxy(_revealer_child_grid)
        revealer_child_grid.add_class("server-names-grid")

        _server_header = ServerHeader(dasbhoard_view.application)
        server_header = weakref.proxy(_server_header)

        row_counter = 0
        for server in country_item.servers:

            add_header = False
            header = server_header.create(server, country_item)
            if header and not display_sc:
                add_header = True
                revealer_child_grid.attach(
                    header.widget, col=0,
                    row=row_counter + 1, width=1, height=1
                )

            row_counter += 1 + (1 if add_header else 0)
            _server_row = ServerRow(
                dasbhoard_view,
                country_item,
                server,
                display_sc
            )
            server_row = weakref.proxy(_server_row)

            revealer_child_grid.attach(
                server_row.event_box,
                row=row_counter
            )

        self.revealer.add(revealer_child_grid.widget)
