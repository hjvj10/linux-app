import gi

gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf, Gtk
from protonvpn_nm_lib.country_codes import country_codes
from protonvpn_nm_lib.enums import FeatureEnum
from ..enums import GLibEventSourceEnum


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

        self.dv.dashboard_view_model.on_sort_conutries_by_tier(
            state.server_list
        )
        self.dv.dashboard_view_model.on_sort_conutries_by_name(
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
        self.server_list_revealer = ServerListRevealer(country_item.servers)

        self.row_grid = Gtk.Grid()
        self.row_grid.set_hexpand(True)
        self.row_grid.set_valign(Gtk.Align.FILL)
        self.row_grid.props.visible = True

        self.row_grid_context = self.row_grid.get_style_context()
        self.row_grid_context.add_class("country-row")

        self.left_child = CountryRowLeftGrid(country_item, self.dv)
        self.right_child = CountryRightGrid(
            country_item, self.server_list_revealer, self.dv
        )

        self.row_grid.attach(self.left_child.grid, 0, 0, 1, 1)
        self.row_grid.attach_next_to(
            self.right_child.grid, self.left_child.grid,
            Gtk.PositionType.RIGHT, 1, 1
        )
        self.row_grid.set_property("has-tooltip", True)
        self.row_grid.connect(
            "query-tooltip", self.on_country_enter,
            self.right_child.connect_country_button
        )

        self.row_grid.attach(self.server_list_revealer.revealer, 0, 1, 1, 1)
        self.create_event_box()

    def create_event_box(self):
        self.event_box = Gtk.EventBox()
        self.event_box.set_visible_window(True)
        self.event_box.add(self.row_grid)
        self.event_box.connect(
            "leave-notify-event", self.on_country_leave,
            self.right_child.connect_country_button
        )
        self.event_box.props.visible = True

    def on_country_enter(
        self, widget, x, y, keyboard_mode, tooltip, gtk_button
    ):
        """Show connect button on enter country row."""
        gtk_button.props.visible = True

    def on_country_leave(self, gtk_event_box, gtk_even_crossing, gtk_button):
        """Hide connect button on leave country row."""
        gtk_button.props.visible = False


class CountryRowLeftGrid:
    country_flag_size = (15, 15)

    def __init__(self, country_item, dashboard_view):
        self.dv = dashboard_view
        self.grid = Gtk.Grid()
        self.grid.set_hexpand(True)
        self.grid.set_halign(Gtk.Align.START)
        self.grid.set_valign(Gtk.Align.CENTER)
        self.grid.props.visible = True

        self.create_country_flag(country_item.entry_country_code)
        self.create_country_name_label(country_item.country_name)
        self.grid.attach(self.country_flag, 0, 0, 1, 1)
        self.grid.attach_next_to(
            self.country_name, self.country_flag,
            Gtk.PositionType.RIGHT, 1, 1
        )

    def create_country_flag(self, country_code):
        self.country_flag = Gtk.Image()
        self.country_flag.set_valign(Gtk.Align.CENTER)
        self.country_flag_ctx = self.country_flag.get_style_context()
        self.country_flag_ctx.add_class("country-flag")
        w, h = self.country_flag_size
        try:
            self.country_flag.set_from_pixbuf(
                self.dv.create_image_pixbuf_from_name(
                    "flags/small/" + country_code.lower() + ".png",
                    width=w, height=h
                )
            )
        except gi.repository.GLib.Error:
            pass
        self.country_flag.props.visible = True

    def create_country_name_label(self, country_name):
        self.country_name = Gtk.Label(country_name)
        self.country_name.set_valign(Gtk.Align.CENTER)
        self.country_name.props.visible = True


class CountryRightGrid:
    def __init__(self, country_item, revealer, dashboard_view):
        self.dv = dashboard_view
        self.feature_icon_list = []
        self.revealer = revealer
        self.grid = Gtk.Grid()
        self.grid.set_hexpand(False)
        self.grid.set_halign(Gtk.Align.END)
        self.grid.set_valign(Gtk.Align.CENTER)
        self.grid.props.visible = True

        self.create_connect_country_button()
        self.create_chevron_button()
        self.create_chevron_image()
        self.grid.attach(
            self.chevron_button, 0, 0, 1, 1
        )
        self.connect_callback(country_item)
        self.set_country_features(country_item.features)
        self.attach_connect_button()

    def connect_callback(self, country_item):
        self.connect_country_button.connect(
            "clicked", self.connect_to_country,
            country_item.entry_country_code
        )
        self.chevron_button.connect(
            "clicked", self.on_click_chevron,
            self.chevron_image, self.chevron_button_ctx,
            self.revealer.revealer
        )

    def set_country_features(self, country_features):
        feature_to_img_dict = {
            FeatureEnum.TOR: "tor-onion.png",
            FeatureEnum.P2P: "p2p-arrows.png",
        }
        features = list(set(
            [FeatureEnum.TOR, FeatureEnum.P2P]
        ) & set(country_features))

        if len(features) < 1:
            return

        for feature in features:
            pixbuf_feature_icon = self.create_feature_icon(
                feature, feature_to_img_dict
            )
            self.add_css_to_pixbuf_feature_icon(pixbuf_feature_icon)
            self.attach_feature_icon(pixbuf_feature_icon)

    def create_feature_icon(self, feature, feature_to_img_dict):
        feature_icon = Gtk.Image()
        feature_icon.props.visible = True
        feature_icon.set_from_pixbuf(
            self.dv.create_icon_pixbuf_from_name(
                feature_to_img_dict[feature],
                width=20, height=20
            )
        )
        return feature_icon

    def attach_feature_icon(self, pixbuf_feature_icon):
        if len(self.feature_icon_list) < 1:
            self.grid.attach_next_to(
                pixbuf_feature_icon, self.chevron_button,
                Gtk.PositionType.LEFT, 1, 1
            )
        else:
            gtk_image = self.feature_icon_list[-1]
            self.grid.attach_next_to(
                pixbuf_feature_icon, gtk_image,
                Gtk.PositionType.LEFT, 1, 1
            )

        self.feature_icon_list.append(pixbuf_feature_icon)

    def add_css_to_pixbuf_feature_icon(self, pixbuf_feature_icon):
        feature_icon_context = pixbuf_feature_icon.get_style_context()
        feature_icon_context.add_class("country-feature")

    def attach_connect_button(self):
        if len(self.feature_icon_list) >= 1:
            self.grid.attach_next_to(
                self.connect_country_button, self.feature_icon_list[-1],
                Gtk.PositionType.LEFT, 1, 1
            )
            return

        self.grid.attach_next_to(
            self.connect_country_button, self.chevron_button,
            Gtk.PositionType.LEFT, 1, 1
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
        if chevron_btn_ctx.has_class("chevron-unfold"):
            chevron_btn_ctx.remove_class("chevron-unfold")
            chevron_btn_ctx.add_class("chevron-fold")
            revealer.set_reveal_child(True)
            chevron_pixbuf = self.dv.create_icon_pixbuf_from_name(
                "chevron-hover.svg",
                width=25, height=25
            ).rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
        else:
            chevron_btn_ctx.remove_class("chevron-fold")
            chevron_btn_ctx.add_class("chevron-unfold")
            revealer.set_reveal_child(False)
            chevron_pixbuf = self.dv.create_icon_pixbuf_from_name(
                "chevron-default.svg",
                width=25, height=25
            ).rotate_simple(GdkPixbuf.PixbufRotation.NONE)

        gtk_chevron_img.set_from_pixbuf(chevron_pixbuf)

    def create_connect_country_button(self):
        self.connect_country_button = Gtk.Button("CONNECT")
        self.connect_country_button.set_hexpand(True)
        self.connect_country_button.set_halign(Gtk.Align.END)
        self.connect_country_button.set_valign(Gtk.Align.CENTER)
        self.connect_country_button_ctx = self\
            .connect_country_button.get_style_context()
        self.connect_country_button_ctx.add_class("transparent")

    def create_chevron_button(self):
        self.chevron_button = Gtk.Button()
        self.chevron_button.set_valign(Gtk.Align.CENTER)
        self.chevron_button.set_hexpand(True)
        self.chevron_button.set_halign(Gtk.Align.END)
        self.chevron_button.props.visible = True

        self.chevron_button_ctx = self.chevron_button.get_style_context()
        self.chevron_button_ctx.add_class("chevron-unfold")

    def create_chevron_image(self):
        self.chevron_image = Gtk.Image()
        self.chevron_image.set_from_pixbuf(
            self.dv.create_icon_pixbuf_from_name(
                "chevron-default.svg",
                width=25, height=25
            )
        )
        self.chevron_image.props.visible = True
        self.chevron_button.set_image(self.chevron_image)


class ServerListRevealer:
    _row_counter = 0

    def __init__(self, servers):
        self.revealer = Gtk.Revealer()
        self.revealer.set_reveal_child(False)
        self.revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_DOWN
        )
        self.revealer.props.visible = True

        self.revealer_child_grid = Gtk.Grid()
        self.revealer_child_grid.props.visible = True

        for server in servers:
            _server = ServerRow(server)
            self.revealer_child_grid.attach(
                _server.server_row_grid, 0, self._row_counter, 1, 1
            )
            self._row_counter += 1

        self.revealer.add(self.revealer_child_grid)


class ServerRow:
    def __init__(self, server):
        self.server_row_grid = Gtk.Grid()
        self.servername_label = Gtk.Label(server.name)
        self.servername_label = Gtk.Label(server.name)
        self.servername_label.props.visible = True

        self.server_row_grid.attach(self.servername_label, 0, 0, 1, 1)
        self.server_row_grid.props.visible = True
