import gi

gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf, Gtk
from protonvpn_nm_lib.enums import (FeatureEnum, ServerStatusEnum,
                                    ServerTierEnum)

from ..enums import GLibEventSourceEnum
from ..factory import WidgetFactory
from .dialog import ConnectUpgradeDialog
from .server_load import ServerLoad
from .server_features import PremiumCountries, ServerFeaturesView


class ServerListView:
    """ServerList class.

    Setup the server list.
    """
    def __init__(self, dashboard_view, state):
        self.__country_rows = 0
        self.dv = dashboard_view
        self.__server_list = state.server_list
        self.__country_widget_position_tracker = {}
        self.__header_tracker = []
        self.__populate()

    @property
    def total_of_existing_countries(self):
        return self.__country_rows

    def __populate(self):
        self.__attach_countries()

    def __attach_countries(self):
        replaceable_child_grid = WidgetFactory.grid("dummy")
        replaceable_child_grid.show = True

        if self.dv.server_list_grid.get_child_at(0, 0):
            self.dv.server_list_grid.remove_row(0)
        self.dv.server_list_grid.attach(
            replaceable_child_grid.widget, 0, 0, 1, 1
        )

        country_header = CountryHeader(self.dv.application)
        row_counter = 0
        for country_item in self.__server_list.servers:
            if len(country_item) < 1:
                continue

            add_header = False
            header = country_header.create(
                country_item,
                self.__server_list
            )
            if header and not self.__server_list.display_secure_core:
                add_header = True
                replaceable_child_grid.attach(
                    header.widget, col=0,
                    row=row_counter + 1, width=1, height=1
                )
                self.__header_tracker.append(header)

            country_grid_row = CountryRow(
                country_item, self.dv,
                display_sc=self.__server_list.display_secure_core
            )
            row_counter += 1 + (1 if add_header else 0)

            replaceable_child_grid.attach(
                country_grid_row.event_box, col=0,
                row=row_counter, width=1, height=1
            )
            self.__country_widget_position_tracker[
                country_item.country_name
            ] = country_grid_row

        self.__country_rows = self.__server_list.total_ammount_of_countries

    def _yield_countries(self):
        for country_item in self.__server_list.servers:
            yield country_item

    def filter_server_list(self, user_input):
        filtered_country_widgets = [
            country_row
            for country_name, country_row
            in self.__country_widget_position_tracker.items()
            if user_input.lower() in country_name.lower()
        ]

        self.__set_headers_visilbility(False)
        if len(user_input) < 1:
            self.__set_headers_visilbility(True)

        for _, country_row in self.__country_widget_position_tracker.items():
            country_row.row_grid.show = False
            if country_row in filtered_country_widgets:
                country_row.row_grid.show = True

    def __set_headers_visilbility(self, bool_val):
        """Sets header visibility.

        Ideally the headers should be hidden when a user is performing a search,
        otherwise they should be displayed.
        """
        for header in self.__header_tracker:
            header.show = bool_val


class Header:
    def __init__(self, app):
        self.app = app
        self.__grid = WidgetFactory.grid("default")
        self.__grid.add_class("server-list-country-margin-left")
        self.__grid.add_class("server-list-country-margin-right")
        self.__grid.add_class("country-header")
        self.__grid.add_class("header-background-color")
        self.__header_title = WidgetFactory.label("default")
        self.__button = WidgetFactory.button("header_info")
        self.__button.show = False
        self.__info_icon = WidgetFactory.image("server_feature_info")
        self.__button.custom_content(self.__info_icon.widget)
        self.__attach_widgets()
        self.__button.connect("clicked", self.on_display_premium_features)

    @property
    def widget(self):
        return self.__grid.widget

    def __attach_widgets(self):
        self.__grid.attach(self.__header_title.widget)
        self.__grid.attach_right_next_to(self.__button.widget, self.__header_title.widget)

    @property
    def show(self):
        return self.__grid.show

    @show.setter
    def show(self, newboolval):
        self.__grid.show = newboolval

    @property
    def info_icon_visibility(self):
        return self.__button.show

    @info_icon_visibility.setter
    def info_icon_visibility(self, newboolval):
        self.__button.show = newboolval

    @property
    def title(self):
        return self.__header_title.content

    @title.setter
    def title(self, newvalue):
        self.__header_title.content = newvalue

    def on_display_premium_features(self, gtk_button):
        """Display features for specific tier"""
        active_windows = self.app.get_windows()
        if not any(type(window) == ServerFeaturesView for window in active_windows):
            PremiumCountries(self.app)


class CountryHeader:
    """CountryHeader class.

    Creates country headers mainly based on user tier. Has to be instantiated
    before being used.

    Methods:
        - create(current_country, server_list): will automatically figure out
            if the header should be added or not.
    """
    def __init__(self, application):
        self.app = application
        self.__header_tracker = {}

    def create(self, current_country, server_list):
        """Create country header/separator for respective user tier:

        Args:
            server_list: object that can access the ammount of servers
                for each tier and the actual user tier.
            current_country: country_item object
        """
        create_header_for_matching_tier = {
            ServerTierEnum.FREE: self.__solve_for_free_user,
            ServerTierEnum.BASIC: self.__solve_for_basic_user,
            ServerTierEnum.PLUS_VISIONARY: self.__solve_for_top_tier,
            ServerTierEnum.PM: self.__solve_for_top_tier,
        }

        try:
            return create_header_for_matching_tier[server_list.user_tier](
                current_country, server_list
            )
        except KeyError:
            return None

    def __solve_for_free_user(self, current_country, server_list):
        if (
            ServerTierEnum.FREE not in self.__header_tracker
            and current_country.minimum_country_tier.value < ServerTierEnum.BASIC.value
        ):
            free_header = self.__setup_free_header(server_list.ammount_of_free_countries)
            self.__header_tracker[ServerTierEnum.FREE] = free_header
            return free_header
        elif (
            ServerTierEnum.BASIC not in self.__header_tracker
            and current_country.minimum_country_tier.value >= ServerTierEnum.BASIC.value
        ):
            basic_and_plus = self.__setup_basic_and_plus_header(
                server_list.ammount_of_basic_countries + server_list.ammount_of_plus_countries
            )
            self.__header_tracker[ServerTierEnum.BASIC] = basic_and_plus
            return basic_and_plus

        return None

    def __solve_for_basic_user(self, current_country, server_list):
        if (
            ServerTierEnum.BASIC not in self.__header_tracker
            and current_country.minimum_country_tier.value < ServerTierEnum.PLUS_VISIONARY.value
        ):
            basic_header = self.__setup_basic_header(
                server_list.ammount_of_free_countries + server_list.ammount_of_basic_countries
            )
            self.__header_tracker[ServerTierEnum.BASIC] = basic_header
            return basic_header
        elif (
            ServerTierEnum.PLUS_VISIONARY not in self.__header_tracker
            and current_country.minimum_country_tier.value >= ServerTierEnum.PLUS_VISIONARY.value # noqa
        ):
            plus_header = self.__setup_plus_header(server_list.ammount_of_plus_countries)
            self.__header_tracker[ServerTierEnum.PLUS_VISIONARY] = plus_header
            return plus_header

        return None

    def __solve_for_top_tier(self, current_country, server_list):
        if (
            ServerTierEnum.PLUS_VISIONARY not in self.__header_tracker
            and current_country.minimum_country_tier.value <= ServerTierEnum.PLUS_VISIONARY.value # noqa
        ):
            all_locations_header = self.__setup_all_locations_header(
                server_list.total_ammount_of_countries
            )
            self.__header_tracker[ServerTierEnum.PLUS_VISIONARY] = all_locations_header
            return all_locations_header
        elif (
            ServerTierEnum.PM not in self.__header_tracker
            and current_country.minimum_country_tier == ServerTierEnum.PM
        ):
            internal_header = self.__setup_internal_header(
                server_list.ammount_of_internal_countries
            )
            self.__header_tracker[ServerTierEnum.PM] = internal_header
            return internal_header

        return None

    def __setup_free_header(self, server_count):
        h = Header(self.app)
        h.title = "FREE Locations ({})".format(server_count)
        return h

    def __setup_basic_and_plus_header(self, server_count):
        h = Header(self.app)
        h.title = "BASIC&PLUS Locations ({})".format(server_count)
        h.info_icon_visibility = True
        return h

    def __setup_basic_header(self, server_count):
        h = Header(self.app)
        h.title = "BASIC Locations ({})".format(server_count)
        return h

    def __setup_plus_header(self, server_count):
        h = Header(self.app)
        h.title = "PLUS Locations ({})".format(server_count)
        h.info_icon_visibility = True
        return h

    def __setup_internal_header(self, server_count):
        h = Header(self.app)
        h.title = "Internal ({})".format(server_count)
        return h

    def __setup_all_locations_header(self, server_count):
        h = Header(self.app)
        h.title = "Locations ({})".format(server_count)
        h.info_icon_visibility = True
        return h


class CountryRow:
    def __init__(self, country_item, dashboard_view, display_sc):
        self.country_item = country_item
        self.dv = dashboard_view
        self.server_list_revealer = ServerListRevealer(
            self.dv,
            self.country_item.servers,
            display_sc
        )
        self.row_grid = WidgetFactory.grid("country_row")
        self.left_child = CountryRowLeftGrid(self.country_item, display_sc)
        self.right_child = CountryRowRightGrid(
            self.country_item,
            self.server_list_revealer.revealer,
            self.dv,
            display_sc
        )

        self.row_grid.attach(self.left_child.grid.widget)
        self.row_grid.attach_right_next_to(
            self.right_child.grid.widget,
            self.left_child.grid.widget,
        )
        if self.country_item.status != ServerStatusEnum.UNDER_MAINTENANCE:
            self.row_grid.tooltip = True
            self.row_grid.connect(
                "query-tooltip", self.on_country_enter,
                self.right_child.connect_country_button
            )

            self.row_grid.attach(
                self.server_list_revealer.revealer.widget,
                row=1, width=2
            )
        self.create_event_box()

    @property
    def total_of_existing_servers(self):
        return len(self.country_item.servers)

    def create_event_box(self):
        self.event_box = Gtk.EventBox()
        self.event_box.set_visible_window(True)
        self.event_box.add(self.row_grid.widget)
        if self.country_item.status != ServerStatusEnum.UNDER_MAINTENANCE:
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
    def __init__(self, country_item, display_sc):
        self.grid = WidgetFactory.grid("left_child_in_country_row")
        self.grid.add_class("server-list-country-margin-left")
        try:
            self.country_flag = WidgetFactory.image(
                "small_flag", country_item.entry_country_code
            ).widget
        except gi.repository.GLib.Error:
            self.country_flag = WidgetFactory.image("dummy_small_flag").widget
        self.grid.attach(self.country_flag)

        self.sc_chevron = WidgetFactory.image("secure_core_chevron")
        self.grid.attach_right_next_to(
            self.sc_chevron.widget, self.country_flag
        )

        self.country_name = WidgetFactory.label(
            "country", country_item.country_name
        )

        self.grid.attach_right_next_to(
            self.country_name.widget, self.sc_chevron.widget,
        )
        self.sc_chevron.show = True if display_sc else False


class CountryRowRightGrid:
    def __init__(self, country_item, revealer, dashboard_view, display_sc):
        self.dv = dashboard_view
        self.display_sc = display_sc
        self.feature_icon_list = []
        self.revealer = revealer
        self.grid = WidgetFactory.grid("right_child_in_country_row")
        self.grid.add_class("server-list-country-margin-right")

        self.maintenance_icon = WidgetFactory.image("maintenance_icon")
        self.connect_country_button = WidgetFactory.button("connect_country")
        if all(server.has_to_upgrade for server in country_item.servers):
            self.connect_country_button.label = "UPGRADE"
        self.chevron_button = WidgetFactory.button("chevron")
        self.chevron_icon = WidgetFactory.image("chevron_icon")
        self.chevron_button.image = self.chevron_icon.widget
        self.grid.attach(self.chevron_button.widget)
        self.grid.attach(self.maintenance_icon.widget)

        if country_item.status != ServerStatusEnum.UNDER_MAINTENANCE:
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
            feature_icon = WidgetFactory.image(
                feature_to_img_dict[feature]
            )
            feature_icon.show = False if self.display_sc else True
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

    def connect_callback(self, country_item):
        if not all(server.has_to_upgrade for server in country_item.servers):
            self.connect_country_button.connect(
                "clicked", self.connect_to_country,
                country_item.entry_country_code
            )
        else:
            self.connect_country_button.connect(
                "clicked", self.display_upgrade,
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

    def display_upgrade(self, gtk_button):
        ConnectUpgradeDialog(self.dv.application)


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


class ServerRow:
    def __init__(self, dasbhoard_view, server, display_sc):
        self.dv = dasbhoard_view
        self.grid = WidgetFactory.grid("server_row")
        self.grid.add_class("server-row")
        self.left_child = ServerRowLeftGrid(server, display_sc)
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
    def __init__(self, server, display_sc):
        self.feature_icon_list = []
        self.server = server
        self.display_sc = display_sc
        self.grid = WidgetFactory.grid("left_child_in_server_row")
        self.populate_left_grid()

        if not server.status.value:
            self.servername_label.add_class("disabled-label")

    def populate_left_grid(self):
        self.create_load_icon()
        self.create_exit_flag()
        self.create_servername_label()
        self.create_secure_core_chevron()
        self.set_server_features()
        if self.display_sc:
            return

    def create_load_icon(self):
        self.load_icon = ServerLoad(self.server.load)
        self.load_icon.show_all()
        self.grid.attach(self.load_icon)

    def create_exit_flag(self):
        try:
            self.country_flag = WidgetFactory.image(
                "small_flag", self.server.entry_country_code
            )
        except gi.repository.GLib.Error:
            self.country_flag = WidgetFactory.image("dummy_small_flag")

        self.grid.attach_right_next_to(
            self.country_flag.widget,
            self.load_icon,
        )

        self.country_flag.show = True if self.display_sc else False

    def create_servername_label(self):
        self.servername_label = WidgetFactory.label(
            "server", self.server.name
        )
        if self.display_sc:
            country_name = country_codes.get(
                self.server.entry_country_code,
                self.server.entry_country_code
            )
            self.servername_label.content = "via {}".format(country_name)

        self.grid.attach_right_next_to(
            self.servername_label.widget,
            self.country_flag.widget,
        )

    def create_secure_core_chevron(self):
        self.sc_chevron = WidgetFactory.image("secure_core_chevron")
        self.grid.attach_right_next_to(
            self.sc_chevron.widget,
            self.servername_label.widget,
        )
        self.sc_chevron.show = True if self.display_sc else False

    def set_server_features(self):
        feature_to_img_dict = {
            FeatureEnum.TOR: ["tor_icon", "TOR Server"],
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
                pixbuf_feature_icon = WidgetFactory.image(
                    feature_to_img_dict[feature][0]
                )
            except KeyError:
                continue
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
        ConnectUpgradeDialog(self.dv.application)
