import gi
from protonvpn_nm_lib.enums import FeatureEnum, ServerStatusEnum

from ...enums import GLibEventSourceEnum
from ...patterns.factory import WidgetFactory
from ..dialog import ConnectUpgradeDialog
from .server_load import ServerLoad

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from ..server_features import CountryStreamingWidget
import weakref


class ServerRow:
    def __init__(self, dasbhoard_view, country, server, display_sc):
        _grid = WidgetFactory.grid("server_row")
        grid = weakref.proxy(_grid)
        grid.add_class("server-row")

        _left_child = ServerRowLeftGrid(dasbhoard_view, country, server, display_sc)
        left_child = weakref.proxy(_left_child)

        _right_child = ServerRowRightGrid(dasbhoard_view, server)
        right_child = weakref.proxy(_right_child)

        grid.attach(left_child.grid.widget)
        grid.attach_right_next_to(
            right_child.grid.widget,
            left_child.grid.widget,
        )
        self.create_event_box(server, grid, right_child)

    def create_event_box(self, server, grid, right_child):
        self.event_box = Gtk.EventBox()
        self.event_box.set_visible_window(True)
        self.event_box.add(grid.widget)
        self.event_box.props.visible = True

        if server.status == ServerStatusEnum.UNDER_MAINTENANCE:
            return

        self.event_box.connect(
            "enter-notify-event", right_child.on_server_enter
        )
        self.event_box.connect(
            "leave-notify-event", right_child.on_server_leave
        )


class ServerRowLeftGrid:
    def __init__(self, dasbhoard_view, country, server, display_sc):
        self.grid = WidgetFactory.grid("left_child_in_server_row")
        self.server = server
        self.feature_icon_list = []
        self.display_sc = display_sc
        self.populate_left_grid(dasbhoard_view, country)

    def populate_left_grid(self, dasbhoard_view, country):
        _load_icon = self.create_load_icon()
        load_icon = weakref.proxy(_load_icon)

        _country_flag = self.create_exit_flag()
        country_flag = weakref.proxy(_country_flag)

        _servername_label = self.create_servername_label()
        servername_label = weakref.proxy(_servername_label)

        _secure_core_chevron = self.create_secure_core_chevron()
        secure_core_chevron = weakref.proxy(_secure_core_chevron)

        self.grid.attach(load_icon.widget)
        self.grid.attach_right_next_to(
            country_flag.widget,
            load_icon.widget,
        )
        self.grid.attach_right_next_to(
            servername_label.widget,
            country_flag.widget,
        )
        self.grid.attach_right_next_to(
            secure_core_chevron.widget,
            servername_label.widget,
        )
        if not self.display_sc:
            self.set_server_features(dasbhoard_view, country, servername_label)

    def create_load_icon(self):
        load_icon = ServerLoad(self.server.load)
        load_icon.show_all()
        return load_icon

    def create_exit_flag(self):
        try:
            country_flag = WidgetFactory.image(
                "small_flag", self.server.entry_country_code
            )
            country_flag.remove_class("country-flag")
            country_flag.add_class("margin-left-10px")
            country_flag.add_class("margin-right-10px")
        except gi.repository.GLib.Error:
            country_flag = WidgetFactory.image("dummy_small_flag")

        country_flag.show = True if self.display_sc else False

        return country_flag

    def create_servername_label(self):
        servername_label = WidgetFactory.label(
            "server", self.server.name
        )

        if not self.server.status.value:
            servername_label.add_class("disabled-label")

        if self.display_sc:
            from protonvpn_nm_lib.country_codes import country_codes

            country_name = country_codes.get(
                self.server.entry_country_code,
                self.server.entry_country_code
            )
            servername_label.content = "via {}".format(country_name)

        return servername_label

    def create_secure_core_chevron(self):
        sc_chevron = WidgetFactory.image("secure_core_chevron")
        sc_chevron.show = True if self.display_sc else False
        return sc_chevron

    def set_server_features(self, dasbhoard_view, country, servername_label):
        feature_to_img_dict = {
            FeatureEnum.TOR: ["tor_icon", "Tor Server"],
            FeatureEnum.P2P: ["p2p_icon", "P2P Server"],
            FeatureEnum.STREAMING: ["streaming_icon", "Streaming"],
        }

        features = self.server.features
        if len(features) < 1 or len(features) == 1 and (
            FeatureEnum.NORMAL not in features
            or FeatureEnum.SECURE_CORE not in features
        ):
            return

        for feature in features:
            try:
                _pixbuf_feature_icon = WidgetFactory.image(
                    feature_to_img_dict[feature][0]
                )
                pixbuf_feature_icon = weakref.proxy(_pixbuf_feature_icon)
            except KeyError:
                continue
            pixbuf_feature_icon.tooltip = True
            pixbuf_feature_icon.tooltip_text = feature_to_img_dict[feature][1]

            if feature == FeatureEnum.STREAMING:
                _button_ = WidgetFactory.button("server_row_streaming_feature")
                _button = weakref.proxy(_button_)
                _w_ = CountryStreamingWidget(
                    dasbhoard_view.application,
                    country.country_name,
                    country.entry_country_code
                )
                _w = weakref.proxy(_w_)
                _button.custom_content(pixbuf_feature_icon.widget)
                _button.connect(
                    "clicked", _w.display
                )
                pixbuf_feature_icon = _button

            self.attach_feature_icon(pixbuf_feature_icon.widget, servername_label)

    def attach_feature_icon(self, pixbuf_feature_icon, servername_label):
        if len(self.feature_icon_list) < 1:
            self.grid.attach_right_next_to(
                pixbuf_feature_icon,
                servername_label.widget
            )
        else:
            gtk_image = self.feature_icon_list[-1]
            self.grid.attach_right_next_to(pixbuf_feature_icon, gtk_image)

        self.feature_icon_list.append(pixbuf_feature_icon)


class ServerRowRightGrid:
    def __init__(self, dasbhoard_view, server):
        self.dv = dasbhoard_view
        self.grid = WidgetFactory.grid("right_child_in_server_row")

        _maintenance_icon = WidgetFactory.image("maintenance_icon")
        maintenance_icon = weakref.proxy(_maintenance_icon)

        self.connect_server_button = WidgetFactory.button("connect_server")
        self.city_label = WidgetFactory.label("city", server.city)
        maintenance_icon.tooltip = True
        maintenance_icon.tooltip_text = "Under maintenance"
        server_under_maintenance = server.status == ServerStatusEnum.UNDER_MAINTENANCE

        maintenance_icon.show = server_under_maintenance
        self.city_label.show = not server_under_maintenance
        object_to_attach = (
            maintenance_icon
            if server_under_maintenance
            else self.connect_server_button
        )

        # Both widgets are attached to the same position
        # as they are mutually exclusive. Only one at the
        # time can be displayed.
        self.grid.attach(self.city_label.widget)
        self.grid.attach(object_to_attach.widget)

        if server_under_maintenance:
            return

        self.connect_server_button.connect(
            "clicked", self.connect_to_server,
            server.name, server.has_to_upgrade
        )

        if server.has_to_upgrade:
            self.connect_server_button.label = "UPGRADE"
            self.city_label.content = "Upgrade"

    def connect_to_server(self, gtk_button_object, servername, user_has_to_upgrade):
        if user_has_to_upgrade:
            ConnectUpgradeDialog(self.dv.application)
        else:
            self.dv.remove_background_glib(
                GLibEventSourceEnum.ON_MONITOR_VPN
            )
            self.dv.dashboard_view_model.on_servername_connect(servername)

    def on_server_enter(self, gtk_widget, event_crossing):
        """Show connect button on enter country row."""
        self.city_label.show = False
        self.connect_server_button.show = True

    def on_server_leave(self, gtk_widget, event_crossing):
        """Hide connect button on leave country row."""
        if event_crossing.detail in [
            Gdk.NotifyType.NONLINEAR,
            Gdk.NotifyType.NONLINEAR_VIRTUAL,
            Gdk.NotifyType.ANCESTOR,
            Gdk.NotifyType.VIRTUAL
        ]:
            self.connect_server_button.show = False
            self.city_label.show = True
