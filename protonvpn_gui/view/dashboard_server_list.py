import gi

gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf, Gtk
from protonvpn_nm_lib.country_codes import country_codes
from protonvpn_nm_lib.enums import FeatureEnum, ServerStatusEnum
from ..factory import WidgetFactory
from ..enums import GLibEventSourceEnum
from .dialog import DialogView


class DashboardServerList:
    """ServerList class.

    Setup the server list.
    """
    def __init__(self, dashboard_view, state):
        self.dv = dashboard_view
        self.populate_list(state)

    def populate_list(self, state):
        row_counter = 0

        for country_item in state.server_list:
            country_item.country_name = country_codes.get(
                country_item.entry_country_code,
                country_item.entry_country_code
            )

        self.dv.dashboard_view_model.on_sort_countries_by_tier(
            state.server_list
        )
        self.dv.dashboard_view_model.on_sort_countries_by_name(
            state.server_list
        )
        for country_item in state.server_list:
            country_grid_row = CountryRow(country_item, self.dv).event_box
            self.dv.server_list_grid.attach(
                country_grid_row, 0,
                row_counter, 1, 1
            )

            row_counter += 1


class CountryRow:
    def __init__(self, country_item, dashboard_view):
        self.dv = dashboard_view
        self.server_list_revealer = ServerListRevealer(
            self.dv,
            country_item.servers
        )
        self.row_grid = WidgetFactory.grid("country_row")
        self.left_child = CountryRowLeftGrid(country_item)
        self.right_child = CountryRowRightGrid(
            country_item,
            self.server_list_revealer.revealer,
            self.dv
        )

        self.row_grid.attach(self.left_child.grid.widget)
        self.row_grid.attach_right_next_to(
            self.right_child.grid.widget,
            self.left_child.grid.widget,
        )
        if country_item.status != ServerStatusEnum.UNDER_MAINTENANCE:
            self.row_grid.tooltip = True
            self.row_grid.connect(
                "query-tooltip", self.on_country_enter,
                self.right_child.connect_country_button
            )

            self.row_grid.attach(
                self.server_list_revealer.revealer.widget,
                row=1, width=2
            )
        self.create_event_box(country_item)

    def create_event_box(self, country_item):
        self.event_box = Gtk.EventBox()
        self.event_box.set_visible_window(True)
        self.event_box.add(self.row_grid.widget)
        if country_item.status != ServerStatusEnum.UNDER_MAINTENANCE:
            self.event_box.connect(
                "leave-notify-event", self.on_country_leave,
                self.right_child.connect_country_button
            )
        self.event_box.props.visible = True

    def on_country_enter(
        self, widget, x, y, keyboard_mode, tooltip, gtk_button
    ):
        """Show connect button on enter country row."""
        gtk_button.show = True

    def on_country_leave(self, gtk_event_box, gtk_even_crossing, gtk_button):
        """Hide connect button on leave country row."""
        gtk_button.show = False


class CountryRowLeftGrid:
    def __init__(self, country_item):
        self.grid = WidgetFactory.grid("left_child_in_country_row")

        try:
            self.country_flag = WidgetFactory.image(
                "small_flag", country_item.entry_country_code
            ).widget
        except gi.repository.GLib.Error:
            self.country_flag = WidgetFactory.image("dummy_small_flag").widget

        self.country_name = WidgetFactory.label(
            "country", country_item.country_name
        )
        if not country_item.available_to_free_users:
            self.country_name.add_class("disabled-label")
        self.grid.attach(self.country_flag)
        self.grid.attach_right_next_to(
            self.country_name.widget, self.country_flag,
        )


class CountryRowRightGrid:
    def __init__(self, country_item, revealer, dashboard_view):
        self.dv = dashboard_view
        self.feature_icon_list = []
        self.revealer = revealer
        self.grid = WidgetFactory.grid("right_child_in_country_row")

        self.maintenance_icon = WidgetFactory.image("maintenance_icon")
        self.connect_country_button = WidgetFactory.button("connect_country")
        self.chevron_button = WidgetFactory.button("chevron")
        self.chevron_icon = WidgetFactory.image("chevron_icon")
        self.chevron_button.image = self.chevron_icon.widget
        self.grid.attach(self.chevron_button.widget)
        self.grid.attach(self.maintenance_icon.widget)

        if not country_item.available_to_free_users:
            return
        elif country_item.status != ServerStatusEnum.UNDER_MAINTENANCE:
            self.connect_callback(country_item)
            self.attach_connect_button()
            self.set_country_features(country_item.features)
        else:
            self.connect_country_button.show = False
            self.chevron_button.show = False
            self.maintenance_icon.show = True

    def set_country_features(self, country_features):
        feature_to_img_dict = {
            FeatureEnum.TOR: "tor_icon",
            FeatureEnum.P2P: "p2p_icon",
        }
        features = list(set(
            [FeatureEnum.TOR, FeatureEnum.P2P]
        ) & set(country_features))

        if len(features) < 1:
            return

        for feature in features:
            pixbuf_feature_icon = WidgetFactory.image(
                feature_to_img_dict[feature]
            ).widget
            self.attach_feature_icon(pixbuf_feature_icon)

    def attach_feature_icon(self, pixbuf_feature_icon):
        if len(self.feature_icon_list) < 1:
            self.grid.attach_left_next_to(
                pixbuf_feature_icon,
                self.connect_country_button.widget,
            )
        else:
            gtk_image = self.feature_icon_list[-1]
            self.grid.attach_left_next_to(pixbuf_feature_icon, gtk_image)

        self.feature_icon_list.append(pixbuf_feature_icon)

    def attach_connect_button(self):
        self.grid.attach_left_next_to(
            self.connect_country_button.widget,
            self.chevron_button.widget,
        )

    def connect_callback(self, country_item):
        self.connect_country_button.connect(
            "clicked", self.connect_to_country,
            country_item.entry_country_code
        )
        self.chevron_button.connect(
            "clicked", self.on_click_chevron,
            self.chevron_icon.widget, self.chevron_button.context,
            self.revealer.widget
        )

    def connect_to_country(self, gtk_button_object, country_code):
        self.dv.remove_background_glib(
            GLibEventSourceEnum.ON_MONITOR_VPN
        )
        self.dv.dashboard_view_model.on_country_connect(country_code)

    def on_click_chevron(
        self, gtk_button_object,
        gtk_chevron_img, chevron_btn_ctx,
        revealer
    ):
        dummy_object = WidgetFactory.image("dummy")
        if chevron_btn_ctx.has_class("chevron-unfold"):
            chevron_btn_ctx.remove_class("chevron-unfold")
            chevron_btn_ctx.add_class("chevron-fold")
            revealer.set_reveal_child(True)
            chevron_pixbuf = dummy_object.create_icon_pixbuf_from_name(
                "chevron-hover.svg",
                width=25, height=25
            ).rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
        else:
            chevron_btn_ctx.remove_class("chevron-fold")
            chevron_btn_ctx.add_class("chevron-unfold")
            revealer.set_reveal_child(False)
            chevron_pixbuf = dummy_object.create_icon_pixbuf_from_name(
                "chevron-default.svg",
                width=25, height=25
            ).rotate_simple(GdkPixbuf.PixbufRotation.NONE)

        gtk_chevron_img.set_from_pixbuf(chevron_pixbuf)


class ServerListRevealer:
    _row_counter = 0

    def __init__(self, dasbhoard_view, servers):
        self.dv = dasbhoard_view
        self.revealer = WidgetFactory.revealer("server_list")
        self.revealer_child_grid = WidgetFactory.grid("revealer_child")

        for server in servers:
            self.revealer_child_grid.attach(
                ServerRow(self.dv, server).event_box,
                row=self._row_counter
            )
            self._row_counter += 1

        self.revealer.add(self.revealer_child_grid.widget)


class ServerRow:
    def __init__(self, dasbhoard_view, server):
        self.dv = dasbhoard_view
        self.grid = WidgetFactory.grid("server_row")
        self.left_child = ServerRowLeftGrid(server)
        self.right_child = ServerRowRightGrid(self.dv, server)
        self.grid.attach(self.left_child.grid.widget)
        self.grid.attach_right_next_to(
            self.right_child.grid.widget,
            self.left_child.grid.widget,
        )
        if server.status != ServerStatusEnum.UNDER_MAINTENANCE:
            self.grid.tooltip = True
            self.grid.connect(
                "query-tooltip", self.on_server_enter,
                self.right_child.connect_server_button,
                self.right_child.city_label
            )
        self.create_event_box(server)

    def create_event_box(self, server):
        self.event_box = Gtk.EventBox()
        self.event_box.set_visible_window(True)
        self.event_box.add(self.grid.widget)
        if server.status != ServerStatusEnum.UNDER_MAINTENANCE:
            self.event_box.connect(
                "leave-notify-event", self.on_server_leave,
                self.right_child.connect_server_button,
                self.right_child.city_label,
            )
        self.event_box.props.visible = True

    def on_server_enter(
        self, widget, x, y, keyboard_mode, tooltip, connect_button, city_label
    ):
        """Show connect button on enter country row."""
        city_label.show = False
        connect_button.show = True

    def on_server_leave(
        self, gtk_event_box, gtk_event_crossing, connect_button, city_label
    ):
        """Hide connect button on leave country row."""
        connect_button.show = False
        city_label.show = True


class ServerRowLeftGrid:
    def __init__(self, server):
        self.feature_icon_list = []
        self.grid = WidgetFactory.grid("left_child_in_server_row")

        self.load_icon = WidgetFactory.image(
            "load_icon_flag",
            "{}% Load".format(
                server.load
            )
        )

        self.grid.attach(self.load_icon.widget)
        self.create_servername_label(server.name)
        self.set_server_features(server.features)
        self.create_is_plus_server_icon(server.is_plus)
        if not server.status.value:
            self.servername_label.add_class("disabled-label")

    def create_servername_label(self, servername):
        self.servername_label = WidgetFactory.label("server", servername)
        self.grid.attach_right_next_to(
            self.servername_label.widget,
            self.load_icon.widget,
        )

    def create_is_plus_server_icon(self, is_plus_server):
        if not is_plus_server:
            return

        plus_server_icon = WidgetFactory.image("plus_icon")
        plus_server_icon.tooltip = True
        plus_server_icon.tooltip_text = "Plus Server"
        if len(self.feature_icon_list) < 1:
            self.grid.attach_right_next_to(
                plus_server_icon.widget,
                self.servername_label.widget,
            )
            return

        self.grid.attach_right_next_to(
            plus_server_icon.widget,
            self.feature_icon_list[-1],
        )

    def set_server_features(self, server_features):
        feature_to_img_dict = {
            FeatureEnum.TOR: ["tor_icon", "TOR Server"],
            FeatureEnum.P2P: ["p2p_icon", "P2P Server"],
        }
        features = list(set(
            [FeatureEnum.TOR, FeatureEnum.P2P]
        ) & set(server_features))

        if len(features) < 1:
            return

        for feature in features:
            pixbuf_feature_icon = WidgetFactory.image(
                feature_to_img_dict[feature][0]
            )
            pixbuf_feature_icon.tooltip = True
            pixbuf_feature_icon.tooltip_text = feature_to_img_dict[feature][1]
            self.attach_feature_icon(pixbuf_feature_icon.widget)

    def attach_feature_icon(self, pixbuf_feature_icon):
        if len(self.feature_icon_list) < 1:
            self.grid.attach_right_next_to(
                pixbuf_feature_icon,
                self.servername_label.widget
            )
        else:
            gtk_image = self.feature_icon_list[-1]
            self.grid.attach_right_next_to(pixbuf_feature_icon, gtk_image)

        self.feature_icon_list.append(pixbuf_feature_icon)


class ServerRowRightGrid:
    def __init__(self, dasbhoard_view, server):
        self.dv = dasbhoard_view
        self.grid = WidgetFactory.grid("right_child_in_server_row")
        self.maintenance_icon = WidgetFactory.image("maintenance_icon")
        self.connect_server_button = WidgetFactory.button("connect_server")
        self.city_label = WidgetFactory.label("city", server.city)
        self.maintenance_icon.tooltip = True
        self.maintenance_icon.tooltip_text = "Under maintenance"

        if server.status == ServerStatusEnum.UNDER_MAINTENANCE:
            self.maintenance_icon.show = True
            self.connect_server_button.show = False
            self.city_label.show = False
            object_to_attach = self.maintenance_icon
        else:
            object_to_attach = self.connect_server_button

            if server.has_to_upgrade:
                self.connect_server_button.label = "UPGRADE"
                self.city_label = WidgetFactory.label(
                    "city", "Upgrade"
                )
                self.connect_server_button.connect(
                    "clicked", self.display_upgrade
                )
            else:
                self.connect_server_button.connect(
                    "clicked", self.connect_to_server,
                    server.name
                )

        # Both widgets are attached to the same position
        # as they are mutually exclusive. Only one at the
        # time can be displayed.
        self.grid.attach(self.city_label.widget)
        self.grid.attach(object_to_attach.widget)

    def connect_to_server(self, gtk_button_object, servername):
        self.dv.remove_background_glib(
            GLibEventSourceEnum.ON_MONITOR_VPN
        )
        self.dv.dashboard_view_model.on_servername_connect(servername)

    def display_upgrade(self, gtk_button_object):
        dialog = DialogView(self.dv.application)
        dialog.display_upgrade()
