import os

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk
from protonvpn_nm_lib.constants import SUPPORTED_PROTOCOLS
from protonvpn_nm_lib.country_codes import country_codes
from protonvpn_nm_lib.enums import ProtocolImplementationEnum

from ..constants import (CSS_DIR_PATH, ICON_DIR_PATH, IMG_DIR_PATH,
                         KILLSWITCH_ICON_SET, NETSHIELD_ICON_SET,
                         SECURE_CORE_ICON_SET, UI_DIR_PATH)
from ..enums import (DashboardFeaturesEnum, DashboardKillSwitchIconEnum,
                     DashboardNetshieldIconEnum, DashboardSecureCoreIconEnum,
                     GLibEventSourceEnum)
from ..logger import logger
from ..view_model.dashboard import (ConnectedToVPNInfo, ConnectError,
                                    ConnectInProgressInfo,
                                    ConnectPreparingInfo, Loading,
                                    NetworkSpeed, NotConnectedToVPNInfo)


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "dashboard.ui"))
class DashboardView(Gtk.ApplicationWindow):
    __gtype_name__ = 'DashboardView'

    # Objects
    headerbar = Gtk.Template.Child()
    dashboard_popover_menu = Gtk.Template.Child()

    overlay_spinner = Gtk.Template.Child()
    connecting_overlay_spinner = Gtk.Template.Child()

    headerbar_menu_button = Gtk.Template.Child()
    main_dashboard_button = Gtk.Template.Child()
    cancel_connect_overlay_button = Gtk.Template.Child()

    connecting_progress_bar = Gtk.Template.Child()

    # Labels
    country_servername_label = Gtk.Template.Child()
    ip_label = Gtk.Template.Child()
    serverload_label = Gtk.Template.Child()
    download_speed_label = Gtk.Template.Child()
    connected_protocol_label = Gtk.Template.Child()
    upload_speed_label = Gtk.Template.Child()
    overlay_bottom_label = Gtk.Template.Child()
    connecting_to_label = Gtk.Template.Child()
    connecting_to_country_servername_label = Gtk.Template.Child()

    # Images/Icons
    headerbar_sign_icon = Gtk.Template.Child()
    overlay_logo_image = Gtk.Template.Child()
    server_load_image = Gtk.Template.Child()
    download_speed_image = Gtk.Template.Child()
    upload_speed_image = Gtk.Template.Child()
    sidebar_country_image = Gtk.Template.Child()
    dashboard_secure_core_button_image = Gtk.Template.Child()
    dashboard_netshield_button_image = Gtk.Template.Child()
    dashboard_killswitch_button_image = Gtk.Template.Child()

    # Grids
    connected_label_grid = Gtk.Template.Child()
    ip_label_grid = Gtk.Template.Child()
    ip_server_load_labels_grid = Gtk.Template.Child()
    connection_information_grid = Gtk.Template.Child()
    connection_speed_label_grid = Gtk.Template.Child()

    # Boxes
    overlay_box = Gtk.Template.Child()
    connecting_overlay_box = Gtk.Template.Child()

    # Constants
    feature_button_icon_width = 20
    feature_button_icon_height = 20
    on_network_speed_update_seconds = 1
    on_vpn_monitor_update_seconds = 10
    on_server_load_update_seconds = 900

    glib_source_tracker = {
        GLibEventSourceEnum.ON_MONITOR_VPN: None,
        GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED: None,
        GLibEventSourceEnum.ON_SERVER_LOAD: None,
    }
    glib_source_updated_time = {
        GLibEventSourceEnum.ON_MONITOR_VPN:
            on_vpn_monitor_update_seconds,
        GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED:
            on_network_speed_update_seconds,
        GLibEventSourceEnum.ON_SERVER_LOAD:
            on_server_load_update_seconds,
    }

    features_icon_set_dict = {
        DashboardFeaturesEnum.KILLSWITCH: KILLSWITCH_ICON_SET,
        DashboardFeaturesEnum.NETSHIELD: NETSHIELD_ICON_SET,
        DashboardFeaturesEnum.SECURE_CORE: SECURE_CORE_ICON_SET
    }

    def __init__(self, **kwargs):
        self.dashboard_view_model = kwargs.pop("view_model")
        self.dashboard_view_model.state.subscribe(
            lambda state: GLib.idle_add(self.render_view_state, state)
        )
        super().__init__(**kwargs)
        self.overlay_spinner.set_property("width-request", 200)
        self.overlay_spinner.set_property("height-request", 200)
        self.connecting_overlay_spinner.set_property("width-request", 200)
        self.connecting_overlay_spinner.set_property("height-request", 200)
        self.SET_UI_NOT_CONNECTED = {
            "property": "visible",
            "objects": [
                (self.download_speed_label, False),
                (self.download_speed_image, False),
                (self.upload_speed_image, False),
                (self.upload_speed_label, False),
                (self.connected_protocol_label, False),
                (self.serverload_label, False),
                (self.sidebar_country_image, False),
                (self.server_load_image, False),
                (self.connecting_overlay_box, False),
                (self.overlay_box, False),
            ]
        }
        self.SET_UI_CONNECTED = {
            "property": "visible",
            "objects": [
                (self.connected_protocol_label, True),
                (self.download_speed_label, True),
                (self.download_speed_image, True),
                (self.upload_speed_image, True),
                (self.upload_speed_label, True),
                (self.serverload_label, True),
                (self.sidebar_country_image, True),
                (self.server_load_image, False),
                (self.connecting_overlay_box, False),
                (self.overlay_box, False),
            ]
        }
        self.overlay_box_context = self.overlay_box.get_style_context()
        self.glib_source_updated_method = {
            GLibEventSourceEnum.ON_MONITOR_VPN:
                self.dashboard_view_model.on_monitor_vpn,
            GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED:
                self.dashboard_view_model.on_update_speed,
            GLibEventSourceEnum.ON_SERVER_LOAD:
                self.dashboard_view_model.on_update_server_load,
        }
        self.setup_icons_images()
        self.setup_css()
        self.setup_actions()
        self.dashboard_view_model.on_startup()

    def on_click_disconnect(self, gtk_button_object):
        logger.info("Clicked on disconnect")
        self.remove_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        self.remove_background_glib(
            GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED
        )
        self.dashboard_view_model.on_disconnect()

    def on_click_quick_connect(self, gtk_button_object):
        logger.info("Clicked on quick connect")
        self.remove_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        self.dashboard_view_model.on_quick_connect()

    def render_view_state(self, state):
        if isinstance(state, Loading):
            InitLoad(self, state)
        elif isinstance(state, NotConnectedToVPNInfo):
            NotConnectedVPN(self, state)
        elif isinstance(state, ConnectPreparingInfo):
            ConnectVPNPreparing(self, state)
        elif isinstance(state, ConnectInProgressInfo):
            ConnectVPNInProgress(self, state)
        elif isinstance(state, ConnectedToVPNInfo):
            ConnectedVPN(self, state)
        elif isinstance(state, ConnectError):
            ConnectVPNError(self, state)
        elif isinstance(state, NetworkSpeed):
            self.upload_speed_label.props.label = state.upload + " B/s"
            self.download_speed_label.props.label = state.download + " B/s"

    def on_click_hide_connect_overlay(
        self, gtk_button_object, gio_task_object
    ):
        self.gtk_property_setter(self.SET_UI_NOT_CONNECTED)

    def gtk_property_setter(self, *args):
        for property_group in args:
            property = property_group.get("property")
            objects = property_group.get("objects")
            for object in objects:
                gtk_object, value = object
                gtk_object.set_property(property, value)

    def on_display_popover(self, gio_simple_action, _):
        self.dashboard_popover_menu.popup()

    def setup_icons_images(self):
        logger.info("Setting up dashboard images and icons")

        # Get pixbuf objects
        protonvpn_headerbar_pixbuf = self.get_icon_pixbuf(
            "protonvpn-sign-green.svg",
            width=50, height=50,
        )
        logo_pixbuf = self.get_image_pixbuf(
            "protonvpn-logo-white.svg",
            width=325, height=250
        )
        window_icon = self.get_icon_pixbuf(
            "protonvpn_logo.png",
        )
        upload_pixbuff = self.get_icon_pixbuf(
            "down-icon.svg",
            width=15, height=15
        )
        download_pixbuff = self.get_icon_pixbuf(
            "up-icon.svg",
            width=15, height=15
        )
        feature_button_secure_core_pixbuf = self.get_icon_pixbuf(
            self.features_icon_set_dict[
                DashboardFeaturesEnum.SECURE_CORE
            ][DashboardSecureCoreIconEnum.OFF],
            width=self.feature_button_icon_width,
            height=self.feature_button_icon_height
        )
        feature_button_netshield_pixbuf = self.get_icon_pixbuf(
            self.features_icon_set_dict[
                DashboardFeaturesEnum.NETSHIELD
            ][DashboardNetshieldIconEnum.OFF],
            width=self.feature_button_icon_width,
            height=self.feature_button_icon_height
        )
        feature_button_killswitch_pixbuf = self.get_icon_pixbuf(
            self.features_icon_set_dict[
                DashboardFeaturesEnum.KILLSWITCH
            ][DashboardKillSwitchIconEnum.OFF],
            width=self.feature_button_icon_width,
            height=self.feature_button_icon_height
        )

        # Set images and icons
        self.headerbar_sign_icon.set_from_pixbuf(protonvpn_headerbar_pixbuf)
        self.overlay_logo_image.set_from_pixbuf(logo_pixbuf)
        self.download_speed_image.set_from_pixbuf(download_pixbuff)
        self.upload_speed_image.set_from_pixbuf(upload_pixbuff)
        self.dashboard_secure_core_button_image.set_from_pixbuf(
            feature_button_secure_core_pixbuf
        )
        self.dashboard_netshield_button_image.set_from_pixbuf(
            feature_button_netshield_pixbuf
        )
        self.dashboard_killswitch_button_image.set_from_pixbuf(
            feature_button_killswitch_pixbuf
        )

        self.set_icon(window_icon)

    def get_icon_pixbuf(
        self, icon_name, width=None, height=None
    ):
        if width and height:
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=os.path.join(
                    ICON_DIR_PATH,
                    icon_name,

                ),
                width=width,
                height=height,
                preserve_aspect_ratio=True
            )

        return GdkPixbuf.Pixbuf.new_from_file(
            filename=os.path.join(
                ICON_DIR_PATH,
                icon_name
            )
        )

    def get_image_pixbuf(
        self, image_name, width=None, height=None
    ):
        if width and height:
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=os.path.join(
                    IMG_DIR_PATH,
                    image_name
                ),
                width=width,
                height=height,
                preserve_aspect_ratio=True
            )

        return GdkPixbuf.Pixbuf.new_from_file(
            filename=os.path.join(
                IMG_DIR_PATH,
                image_name
            )
        )

    def on_connect_load_sidebar_flag(self, country):
        try:
            matching_code = list({
                country_code: _country
                for country_code, _country
                in country_codes.items()
                if country == _country
            }.keys()).pop().lower()
        except IndexError:
            return

        sidebar_flag_pixbuff = self.get_image_pixbuf(
            "sidebar-flags/" + matching_code + ".jpg",
            width=400,
            height=400,
        )
        self.sidebar_country_image.set_from_pixbuf(sidebar_flag_pixbuff)

    def setup_css(self):
        logger.info("Setting up css")
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(
            os.path.join(CSS_DIR_PATH, "dashboard.css")
        )
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def setup_actions(self):
        logger.info("Setting up actions")

        # create action
        headerbar_menu = Gio.SimpleAction.new("show_menu", None)
        cancel_connect_overlay_button = Gio.SimpleAction.new(
            "close_connect_overlay", None
        )

        # connect action to callback
        headerbar_menu.connect("activate", self.on_display_popover)
        cancel_connect_overlay_button.connect(
            "activate", self.on_click_hide_connect_overlay
        )

        # add action
        self.add_action(headerbar_menu)
        self.add_action(cancel_connect_overlay_button)

    def add_background_glib(self, glib_source_type: GLibEventSourceEnum):
        if self.glib_source_tracker[
                glib_source_type
        ] == None:
            logger.debug(
                "{} does not exist, adding it.".format(glib_source_type)
            )
            self.glib_source_tracker[
                glib_source_type
            ] = GLib.timeout_add_seconds(
                self.glib_source_updated_time[glib_source_type],
                self.glib_source_updated_method[glib_source_type]
            )

    def remove_background_glib(self, glib_source_type: GLibEventSourceEnum):
        if self.glib_source_tracker[glib_source_type]:
            logger.debug("{} exists, removing source".format(glib_source_type))
            GLib.source_remove(
                self.glib_source_tracker[
                    glib_source_type
                ]
            )
            self.glib_source_tracker[
                glib_source_type
            ] = None


class InitLoad:
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.overlay_bottom_label.props.label = ""\
            "Secure Internet Anywhere"
        dv.overlay_spinner.start()
        dv.overlay_box.props.visible = True


class NotConnectedVPN:
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        label = "You are not connected"
        ip = state.ip
        if state.ip is None:
            label = "Network issues detected."
            ip = "None"

        dv.country_servername_label.props.label = \
            label
        dv.ip_label.props.label = ip
        label_ctx = dv.country_servername_label.get_style_context()
        button_ctx = dv.main_dashboard_button.get_style_context()
        if not label_ctx.has_class("warning-color"):
            label_ctx.add_class("warning-color")
        if button_ctx.has_class("transparent-white"):
            button_ctx.remove_class("transparent-white")
        if not button_ctx.has_class("transparent"):
            button_ctx.add_class("transparent")

        try:
            dv.main_dashboard_button.disconnect_by_func(
                dv.on_click_disconnect
            )
        except TypeError:
            pass

        dv.main_dashboard_button.connect(
            "clicked", dv.on_click_quick_connect
        )
        dv.main_dashboard_button.props.label = "Quick Connect"
        dv.add_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        dv.add_background_glib(GLibEventSourceEnum.ON_SERVER_LOAD)
        dv.gtk_property_setter(
            dv.SET_UI_NOT_CONNECTED
        )


class ConnectedVPN:
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        country = "{}".format(state.countries[0])
        country_to_setup_flag = state.countries[0]
        if len(state.countries) > 1:
            country = country + " >> {}".format(
                state.countries[1]
            )
            country_to_setup_flag = state.countries[1]
        dv.on_connect_load_sidebar_flag(country_to_setup_flag)
        country_servername = country + " {}".format(state.servername)
        dv.country_servername_label.props.label = country_servername
        dv.ip_label.props.label = state.ip
        dv.serverload_label.props.label = state.load + "% " + "Load"
        protocol = state.protocol
        if state.protocol in SUPPORTED_PROTOCOLS[
            ProtocolImplementationEnum.OPENVPN
        ]:
            protocol = "OpenVPN ({})".format(
                state.protocol.value.upper()
            )
        dv.connected_protocol_label.props.label = protocol
        label_ctx = dv.country_servername_label.get_style_context()
        button_ctx = dv.main_dashboard_button.get_style_context()

        if label_ctx.has_class("warning-color"):
            label_ctx.remove_class("warning-color")
        if button_ctx.has_class("transparent"):
            button_ctx.remove_class("transparent")
        if not button_ctx.has_class("transparent-white"):
            button_ctx.add_class("transparent-white")

        try:
            dv.main_dashboard_button.disconnect_by_func(
                dv.on_click_quick_connect
            )
        except TypeError:
            pass
        dv.main_dashboard_button.connect(
            "clicked", dv.on_click_disconnect
        )
        dv.main_dashboard_button.props.label = "Disconnect"
        dv.add_background_glib(GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED)
        dv.add_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        dv.add_background_glib(GLibEventSourceEnum.ON_SERVER_LOAD)
        dv.gtk_property_setter(dv.SET_UI_CONNECTED)


class ConnectVPNPreparing:
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.connecting_overlay_spinner.props.visible = True
        dv.connecting_progress_bar.props.visible = True
        dv.connecting_progress_bar.set_fraction(0.2)
        dv.connecting_to_label.props.label = "Preparing ProtonVPN Connection"
        dv.connecting_to_country_servername_label.props.label = ""
        dv.cancel_connect_overlay_button.props.visible = False
        dv.connecting_overlay_box.props.visible = True


class ConnectVPNInProgress:
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        new_value = dv.connecting_progress_bar.get_fraction() + 0.5
        dv.connecting_progress_bar.set_fraction(new_value)
        dv.connecting_to_label.props.label = "Connecting to "
        dv.connecting_to_country_servername_label.props.label = "{} >> "\
            "{}".format(
                state.country, state.servername,
            )


class ConnectVPNError:
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.connecting_to_label.set_text(
            state.message
        )
        dv.cancel_connect_overlay_button.props.visible = True
        dv.cancel_connect_overlay_button.set_label("Close")
        dv.connecting_overlay_spinner.props.visible = False
        dv.connecting_progress_bar.props.visible = False
