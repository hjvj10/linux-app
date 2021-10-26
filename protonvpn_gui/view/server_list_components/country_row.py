import gi
from protonvpn_nm_lib.enums import FeatureEnum, ServerStatusEnum

from ...enums import GLibEventSourceEnum
from ...patterns.factory import WidgetFactory
from ..dialog import ConnectUpgradeDialog
from .revealer import ServerListRevealer

gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf, Gtk, Gdk


class CountryRow:
    def __init__(self, country_item, dashboard_view, display_sc=None):
        self.__num_locations = len(country_item.servers)
        server_list_revealer = ServerListRevealer(
            dashboard_view,
            country_item,
            display_sc
        )
        self.row_grid = WidgetFactory.grid("country_row")
        left_child = CountryRowLeftGrid(country_item, display_sc)
        right_child = CountryRowRightGrid(
            country_item,
            server_list_revealer.revealer,
            dashboard_view,
            display_sc
        )

        self.row_grid.attach(left_child.grid.widget)
        self.row_grid.attach_right_next_to(
            right_child.grid.widget,
            left_child.grid.widget,
        )
        self.create_event_box(country_item, right_child)

        if country_item.status == ServerStatusEnum.UNDER_MAINTENANCE:
            return

        self.row_grid.attach(
            server_list_revealer.revealer.widget,
            row=1, width=2
        )

    @property
    def total_of_existing_servers(self):
        return self.__num_locations

    def create_event_box(self, country_item, right_child):
        self.event_box = Gtk.EventBox()
        self.event_box.set_visible_window(True)
        self.event_box.add(self.row_grid.widget)
        self.event_box.props.visible = True

        if country_item.status == ServerStatusEnum.UNDER_MAINTENANCE:
            return

        self.event_box.connect(
            "enter-notify-event", right_child.on_enter_connect_button
        )
        self.event_box.connect(
            "leave-notify-event", right_child.on_leave_connect_button,
        )


class CountryRowLeftGrid:
    def __init__(self, country_item, display_sc):
        self.grid = WidgetFactory.grid("left_child_in_country_row")
        self.grid.add_class("server-list-country-margin-left")
        self.grid.add_class("country-elements")
        try:
            country_flag = WidgetFactory.image(
                "small_flag", country_item.entry_country_code
            ).widget
        except gi.repository.GLib.Error:
            country_flag = WidgetFactory.image("dummy_small_flag").widget

        self.grid.attach(country_flag)

        sc_chevron = WidgetFactory.image("secure_core_chevron")
        self.grid.attach_right_next_to(
            sc_chevron.widget, country_flag
        )

        country_name = WidgetFactory.label(
            "country", country_item.country_name
        )

        self.grid.attach_right_next_to(
            country_name.widget, sc_chevron.widget,
        )
        sc_chevron.show = True if display_sc else False


class CountryRowRightGrid:
    def __init__(self, country_item, revealer, dashboard_view, display_sc):
        self.dv = dashboard_view
        self.feature_icon_list = []
        country_under_maintenance = country_item.status == ServerStatusEnum.UNDER_MAINTENANCE
        self.grid = WidgetFactory.grid("right_child_in_country_row")
        self.grid.add_class("server-list-country-margin-right")
        self.grid.add_class("country-elements")

        maintenance_icon = WidgetFactory.image("maintenance_icon")
        self.connect_country_button = WidgetFactory.button("connect_country")
        self.chevron_button = WidgetFactory.button("chevron")
        self.chevron_icon = WidgetFactory.image("chevron_icon")
        self.chevron_button.image = self.chevron_icon.widget
        self.grid.attach(self.chevron_button.widget)
        self.grid.attach(maintenance_icon.widget)

        self.chevron_button.show = not country_under_maintenance
        maintenance_icon.show = country_under_maintenance

        if country_under_maintenance:
            return

        self.connect_callback(country_item, revealer)
        self.attach_connect_button()
        self.set_country_features(country_item, display_sc)

    def set_country_features(self, country_item, display_sc):
        feature_to_img_dict = {
            FeatureEnum.TOR: "tor_icon",
            FeatureEnum.P2P: "p2p_icon",
        }
        features = list(
            set(
                [FeatureEnum.TOR, FeatureEnum.P2P]
            ) & set(
                country_item.features
            )
        )

        if country_item.is_virtual:
            feature_icon = WidgetFactory.image("smart_routing_icon")
            self.attach_feature_icon(feature_icon.widget)

        if len(features) < 1:
            return

        for feature in features:
            feature_icon = WidgetFactory.image(
                feature_to_img_dict[feature]
            )
            feature_icon.show = False if display_sc else True
            self.attach_feature_icon(feature_icon.widget)

    def attach_feature_icon(self, feature_icon):
        if len(self.feature_icon_list) < 1:
            self.grid.attach_left_next_to(
                feature_icon,
                self.connect_country_button.widget,
            )
        else:
            gtk_image = self.feature_icon_list[-1]
            self.grid.attach_left_next_to(feature_icon, gtk_image)

        self.feature_icon_list.append(feature_icon)

    def attach_connect_button(self):
        self.grid.attach_left_next_to(
            self.connect_country_button.widget,
            self.chevron_button.widget,
        )

    def connect_callback(self, country_item, revealer):
        if not all(server.has_to_upgrade for server in country_item.servers):
            self.connect_country_button.connect(
                "clicked", self.connect_to_country,
                country_item.entry_country_code
            )
        else:
            self.connect_country_button.connect(
                "clicked", self.display_upgrade,
            )
            self.connect_country_button.label = "UPGRADE"

        self.chevron_button.connect(
            "clicked", self.on_click_chevron,
            self.chevron_icon.widget, self.chevron_button.context,
            revealer.widget
        )

    def on_enter_connect_button(self, gtk_widget, event_crossing):
        self.connect_country_button.show = True

    def on_leave_connect_button(self, gtk_widget, event_crossing):
        if event_crossing.detail in [
            Gdk.NotifyType.NONLINEAR,
            Gdk.NotifyType.NONLINEAR_VIRTUAL,
            Gdk.NotifyType.ANCESTOR,
            Gdk.NotifyType.VIRTUAL
        ]:
            self.connect_country_button.show = False

    def connect_to_country(self, gtk_button_object, country_code):
        self.dv.remove_background_glib(
            GLibEventSourceEnum.ON_MONITOR_VPN
        )
        self.dv.dashboard_view_model.on_country_connect(country_code)

    def on_click_chevron(
        self, gtk_button_object,
        gtk_chevron_icon_widget, chevron_btn_ctx,
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

        gtk_chevron_icon_widget.set_from_pixbuf(chevron_pixbuf)

    def display_upgrade(self, gtk_button):
        ConnectUpgradeDialog(self.dv.application)
