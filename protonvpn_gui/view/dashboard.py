import os

import gi
gi.require_version('Gtk', '3.0')

from protonvpn_nm_lib.api import protonvpn
from gi.repository import Gdk, Gio, GLib, Gtk
from protonvpn_nm_lib.constants import SUPPORTED_PROTOCOLS
from protonvpn_nm_lib.enums import ProtocolImplementationEnum

from ..constants import (CSS_DIR_PATH, KILLSWITCH_ICON_SET, NETSHIELD_ICON_SET,
                         SECURE_CORE_ICON_SET, UI_DIR_PATH, protonvpn_logo)
from ..enums import (DashboardFeaturesEnum, DashboardKillSwitchIconEnum,
                     DashboardNetshieldIconEnum, DashboardSecureCoreIconEnum,
                     GLibEventSourceEnum)
from ..logger import logger
from ..view_model.dashboard import (ConnectedToVPNInfo, ConnectError,
                                    ConnectInProgressInfo,
                                    ConnectPreparingInfo, Loading,
                                    NetworkSpeed, NotConnectedToVPNInfo,
                                    ServerListData, QuickSettingsStatus)
from .server_list import ServerListView
from ..factory import WidgetFactory
from .quick_settings_popover import QuickSettingsPopoverView
# from .custom_tooltip import CustomToolTip
from .server_features import PremiumCountries, ServerFeaturesView


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "dashboard.ui"))
class DashboardView(Gtk.ApplicationWindow):
    """
    Dashboard view. GTK Composite object.

    Renders everything related to the user Dashboard. It's different
    views are managed by the listener dashboard_view_model.state,
    which is updated once certain operations are concluded in the ViewModel.

    Different view types are rendered in the method render_view_state, which
    attempts to match the instance state defined in dashboard_view_model.
    The view types are divided into own classes which receive the current
    instance of DashboardView and the proceed to manipulate the UI. Creating
    new classes was preffered instead of methods to facilitate code reading
    and clear separation of view states.


    Once connections are started or ended, the UI will react accordingly.
    Also, background processes started with Glib.timeout_add_seconds are
    constantly monitored and tracked to make sure that there are no
    multiple background simillar processes running at the same time.
    Ie: Two existing processes which update the network speed each second.
    """
    __gtype_name__ = 'DashboardView'

    # Other objects
    headerbar = Gtk.Template.Child()

    overlay_spinner = Gtk.Template.Child()
    connecting_overlay_spinner = Gtk.Template.Child()
    connecting_progress_bar = Gtk.Template.Child()

    server_list_scrolled_window = Gtk.Template.Child()
    server_list_view_port = Gtk.Template.Child()

    # Popover menus
    dashboard_popover_menu = Gtk.Template.Child()

    # Buttons
    # The button below is not used and is left only for
    # reference that it exists and can be used if wished.
    # headerbar_menu_button = Gtk.Template.Child()
    main_dashboard_button = Gtk.Template.Child()
    cancel_connect_overlay_button = Gtk.Template.Child()
    dashboard_secure_core_button_menu = Gtk.Template.Child()
    dashboard_netshield_button = Gtk.Template.Child()
    dashboard_killswitch_button = Gtk.Template.Child()
    server_search_entry = Gtk.Template.Child()
    servers_info_icon_button = Gtk.Template.Child()

    # Labels
    country_servername_label = Gtk.Template.Child()
    ip_label = Gtk.Template.Child()
    serverload_label = Gtk.Template.Child()
    download_speed_label = Gtk.Template.Child()
    connected_protocol_label = Gtk.Template.Child()
    upload_speed_label = Gtk.Template.Child()
    locations_label = Gtk.Template.Child()
    overlay_bottom_label = Gtk.Template.Child()
    connecting_to_label = Gtk.Template.Child()
    connecting_to_country_servername_label = Gtk.Template.Child()

    # Images/Icons
    headerbar_sign_icon = Gtk.Template.Child()
    overlay_logo_image = Gtk.Template.Child()
    server_load_image = Gtk.Template.Child()
    download_speed_image = Gtk.Template.Child()
    upload_speed_image = Gtk.Template.Child()
    servers_info_icon = Gtk.Template.Child()
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
    top_sever_locations_grid = Gtk.Template.Child()
    server_list_grid = Gtk.Template.Child()

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
        self.application = kwargs.pop("application")

        self.dashboard_view_model.state.subscribe(
            lambda state: GLib.idle_add(self.render_view_state, state)
        )
        self.quick_settings_popover = QuickSettingsPopoverView(
            self.dashboard_view_model
        )
        super().__init__(application=self.application)
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

    def render_view_state(self, state):
        """Render view state.

        State is continuosly being monitored. The state monitor is
        initialized in the __init__ method.
        Based on each instance, it will call a specific class, passing
        the instance of this current object and the state, so that the
        UI can be updated accordingly.
        """
        if isinstance(state, Loading):
            InitLoadView(self, state)
        elif isinstance(state, NotConnectedToVPNInfo):
            NotConnectedVPNView(self, state)
        elif isinstance(state, ConnectPreparingInfo):
            ConnectVPNPreparingView(self, state)
        elif isinstance(state, ConnectInProgressInfo):
            ConnectVPNInProgressView(self, state)
        elif isinstance(state, ConnectedToVPNInfo):
            ConnectedVPNView(self, state)
        elif isinstance(state, ConnectError):
            ConnectVPNErrorView(self, state)
        elif isinstance(state, NetworkSpeed):
            UpdateNetworkSpeedView(self, state)
        elif isinstance(state, ServerListData):
            self.server_list_view = ServerListView(self, state)
        elif isinstance(state, QuickSettingsStatus):
            self.update_quick_settings(state)

    def update_quick_settings(self, state):
        dummy_object = WidgetFactory.image("dummy")
        feature_button_secure_core_pixbuf = dummy_object \
            .create_icon_pixbuf_from_name(
                self.features_icon_set_dict[
                    DashboardFeaturesEnum.SECURE_CORE
                ][state.secure_core],
                width=self.feature_button_icon_width,
                height=self.feature_button_icon_height
            )
        feature_button_netshield_pixbuf = dummy_object \
            .create_icon_pixbuf_from_name(
                self.features_icon_set_dict[
                    DashboardFeaturesEnum.NETSHIELD
                ][state.netshield],
                width=self.feature_button_icon_width,
                height=self.feature_button_icon_height
            )
        feature_button_killswitch_pixbuf = dummy_object \
            .create_icon_pixbuf_from_name(
                self.features_icon_set_dict[
                    DashboardFeaturesEnum.KILLSWITCH
                ][state.killswitch],
                width=self.feature_button_icon_width,
                height=self.feature_button_icon_height
            )

        self.dashboard_secure_core_button_image.set_from_pixbuf(
            feature_button_secure_core_pixbuf
        )
        self.dashboard_netshield_button_image.set_from_pixbuf(
            feature_button_netshield_pixbuf
        )
        self.dashboard_killswitch_button_image.set_from_pixbuf(
            feature_button_killswitch_pixbuf
        )

    def on_click_disconnect(self, gtk_button_object):
        """On click on Disconnect event handler.

        Disconnects from VPN.

        Args:
            gtk_button_object (Gtk.Button)

        """
        logger.info("Clicked on disconnect")
        self.remove_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        self.remove_background_glib(
            GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED
        )
        self.dashboard_view_model.on_disconnect()

    def on_click_quick_connect(self, gtk_button_object):
        """On click Quick Connect event handler.

        Quickly connect to a VPN server.

        Args:
            gtk_button_object (Gtk.Button)
        """
        logger.info("Clicked on quick connect")
        self.remove_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        self.dashboard_view_model.on_quick_connect()

    def on_click_hide_connect_overlay(
        self, gtk_button_object, gio_task_object
    ):
        """On click hides connect overlay.

        If a user attempts to connect to VPN but it fails for some reason,
        the UI is updated accordingly with the message and a close button is
        displayed to the user so that it can close the window and attempt to
        connect again or do other things.
        """
        self.gtk_property_setter(self.SET_UI_NOT_CONNECTED)

    def on_connect_load_sidebar_flag(self, country_code):
        """Loads sidebar flag on connect.

        Loads corresponding country flag to the country.
        Since the ViewModel returns a server object,
        we can easily access the country code.

        If it finds a matching country, it will setup the country
        flag, else it will just return without any errors.

        Args:
            country_code (string): country IS code
        """
        try:
            dummy_object = WidgetFactory.image("dummy")
            sidebar_flag_pixbuff = dummy_object.create_image_pixbuf_from_name(
                "flags/large/" + country_code.lower() + ".jpg",
                width=400, height=400,
            )
        except gi.repository.GLib.Error:
            return

        self.sidebar_country_image.set_from_pixbuf(sidebar_flag_pixbuff)

    def on_display_main_popover_menu(self, gio_simple_action, _):
        """On display main popover event handler.

        Displays top menu popover.

        Args:
            gio_simple_action(Gtk.Action)

        """
        self.dashboard_popover_menu.popup()

    def setup_icons_images(self):
        """Sets up all icons and images at application start.

        All icons and images that need to be loaded and setup
        on window start are managed here. With the only exception
        of the sidebar flag.
        """
        logger.info("Setting up dashboard images and icons")
        dummy_object = WidgetFactory.image("dummy")

        # Get pixbuf objects
        protonvpn_headerbar_pixbuf = dummy_object.create_icon_pixbuf_from_name(
            "protonvpn-sign-green.svg",
            width=50, height=50,
        )
        logo_pixbuf = dummy_object.create_image_pixbuf_from_name(
            "protonvpn-logo-white.svg",
            width=325, height=250
        )
        window_icon = dummy_object.create_icon_pixbuf_from_name(
            protonvpn_logo
        )
        upload_pixbuff = dummy_object.create_icon_pixbuf_from_name(
            "up-icon.svg",
            width=15, height=15
        )
        download_pixbuff = dummy_object.create_icon_pixbuf_from_name(
            "down-icon.svg",
            width=15, height=15
        )
        server_locations_pixbuff = dummy_object.create_icon_pixbuf_from_name(
            "info-circle-filled.svg",
            width=15, height=15
        )
        feature_button_secure_core_pixbuf = dummy_object \
            .create_icon_pixbuf_from_name(
                self.features_icon_set_dict[
                    DashboardFeaturesEnum.SECURE_CORE
                ][DashboardSecureCoreIconEnum.OFF],
                width=self.feature_button_icon_width,
                height=self.feature_button_icon_height
            )
        feature_button_netshield_pixbuf = dummy_object \
            .create_icon_pixbuf_from_name(
                self.features_icon_set_dict[
                    DashboardFeaturesEnum.NETSHIELD
                ][DashboardNetshieldIconEnum.OFF],
                width=self.feature_button_icon_width,
                height=self.feature_button_icon_height
            )
        feature_button_killswitch_pixbuf = dummy_object \
            .create_icon_pixbuf_from_name(
                self.features_icon_set_dict[
                    DashboardFeaturesEnum.KILLSWITCH
                ][DashboardKillSwitchIconEnum.OFF],
                width=self.feature_button_icon_width,
                height=self.feature_button_icon_height
            )

        # Set images and icons
        self.set_icon(window_icon)

        self.headerbar_sign_icon.set_from_pixbuf(protonvpn_headerbar_pixbuf)
        self.overlay_logo_image.set_from_pixbuf(logo_pixbuf)
        self.upload_speed_image.set_from_pixbuf(upload_pixbuff)
        self.download_speed_image.set_from_pixbuf(download_pixbuff)
        self.servers_info_icon.set_from_pixbuf(server_locations_pixbuff)
        self.dashboard_secure_core_button_image.set_from_pixbuf(
            feature_button_secure_core_pixbuf
        )
        self.dashboard_netshield_button_image.set_from_pixbuf(
            feature_button_netshield_pixbuf
        )
        self.dashboard_killswitch_button_image.set_from_pixbuf(
            feature_button_killswitch_pixbuf
        )

    def setup_css(self):
        """Setup CSS styles."""
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
        """Setup actions.

        From documentation:
            Actions represent operations that the user
            can perform, along with some information on
            how it should be presented in the interface.
            Each action provides methods to create icons,
            menu items and toolbar items representing itself.
        (https://developer.gnome.org/gtk3/unstable/GtkAction.html)

        Actions can be mapped to a certain user action (event), instead
        of directly mapping event handlers. Should be used when possible
        to keep UI code portable.
        """
        logger.info("Setting up actions")

        # create action
        cancel_connect_overlay_button = Gio.SimpleAction.new(
            "close_connect_overlay", None
        )
        display_secure_core_popover = Gio.SimpleAction.new(
            "display_secure_core_popover", None
        )
        display_netshield_popover = Gio.SimpleAction.new(
            "display_netshield_popover", None
        )
        display_killswitch_popover = Gio.SimpleAction.new(
            "display_killswitch_popover", None
        )

        # connect action to callback
        cancel_connect_overlay_button.connect(
            "activate", self.on_click_hide_connect_overlay
        )
        display_secure_core_popover.connect(
            "activate",
            self.quick_settings_popover.display_secure_core_settings,
            self.dashboard_secure_core_button_menu
        )
        display_netshield_popover.connect(
            "activate",
            self.quick_settings_popover.display_netshield_settings,
            self.dashboard_netshield_button
        )
        display_killswitch_popover.connect(
            "activate",
            self.quick_settings_popover.display_killswitch_settings,
            self.dashboard_killswitch_button
        )

        # add action
        self.add_action(cancel_connect_overlay_button)
        self.add_action(display_secure_core_popover)
        self.add_action(display_netshield_popover)
        self.add_action(display_killswitch_popover)

        # connect server_search_entry
        self.server_search_entry.connect(
            "search-changed", self.filter_server_list
        )

        # setup events
        self.servers_info_icon_button.connect("clicked", self.on_display_premium_features)

    def on_display_premium_features(self, gtk_button):
        active_windows = self.application.get_windows()
        if not any(type(window) == ServerFeaturesView for window in active_windows):
            PremiumCountries(self.application)

    def filter_server_list(self, server_search_entry):
        """Filter server list based on user input.

        Args:
            server_search_entry: Gtk.SearchEntry
        """
        self.server_list_view.filter_server_list(
            server_search_entry.get_text()
        )

    def gtk_property_setter(self, *args):
        """GTK property setter.

        Args: Following structure:
        {
            "property": "visible",
            "objects": [
                (self.connected_protocol_label, True),
            ]
        }

        Useful to update multiple UI properties in batches.
        Each dict @property value contains the property that
        is desired to change, which then will act on a list of
        @objects. This list contains a tuple, where the first
        argument is the object and the second argument is the value
        that the object property is to be updated to.

        Not useful for only for a couple of UI updates, It is used best
        to update to a certain pre-defined style or state.
        """
        for property_group in args:
            property = property_group.get("property")
            objects = property_group.get("objects")
            for object in objects:
                gtk_object, value = object
                gtk_object.set_property(property, value)

    def add_background_glib(self, glib_source_type: GLibEventSourceEnum):
        """Add background GLib process.

        It intially checks if there is an existent process, so that I does
        not create duplicates (or even more).

        Args:
            glib_source_type (GLibEventSourceEnum)
        """
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
        """Remove background GLib process.

        It intially checks there is an existent process, thus avoiding
        any unnenecessary errors/warnings or crashes.

        Args:
            glib_source_type (GLibEventSourceEnum)
        """
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


class InitLoadView:
    """UI class.

    Setup the UI to an initial loading state (app start).
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.overlay_bottom_label.props.label = ""\
            "Secure Internet Anywhere"
        dv.overlay_spinner.start()
        dv.overlay_box.props.visible = True


class UpdateNetworkSpeedView:
    """UI class.

    Updates network speeds labels.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.upload_speed_label.props.label = state.upload
        dv.download_speed_label.props.label = state.download


class NotConnectedVPNView:
    """UI class.

    Setup the UI to not connected state.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        label = "You are not connected"
        ip = state.ip

        if all(
            attr is None
            for attr
            in [state.ip, state.isp, state.country]
        ):
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


class ConnectedVPNView:
    """UI class.

    Setup the UI to connected state.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        country = protonvpn.get_country()
        country_string = "{}".format(
            country.get_country_name(state.countries[0])
        )
        if len(state.countries) > 1:
            country_string = "{}".format(country.get_country_name(
                state.countries[0]
            ))
            country_string = country_string + " >> {}".format(
                country.get_country_name(state.countries[1])
            )
        dv.on_connect_load_sidebar_flag(state.exit_country_code)
        country_servername = country_string + " {}".format(state.servername)
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


class ConnectVPNPreparingView:
    """UI class.

    Setup the UI during VPN prepare state.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.connecting_overlay_spinner.props.visible = True
        dv.connecting_progress_bar.props.visible = True
        dv.connecting_progress_bar.set_fraction(0.2)
        dv.connecting_to_label.props.label = "Preparing ProtonVPN Connection"
        dv.connecting_to_country_servername_label.props.label = ""
        dv.cancel_connect_overlay_button.props.visible = False
        dv.connecting_overlay_box.props.visible = True


class ConnectVPNInProgressView:
    """UI class.

    Setup the UI during VPN connection in progress state.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        new_value = dv.connecting_progress_bar.get_fraction() + 0.5
        dv.connecting_progress_bar.set_fraction(new_value)
        dv.connecting_to_label.props.label = "Connecting to "
        dv.connecting_to_country_servername_label.props.label = "{} >> "\
            "{}".format(
                state.country, state.servername,
            )


class ConnectVPNErrorView:
    """UI class.

    Setup the UI state when an error occurs
    during attempt to connect.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.connecting_to_label.set_text(
            state.message
        )
        dv.cancel_connect_overlay_button.props.visible = True
        dv.cancel_connect_overlay_button.set_label("Close")
        dv.connecting_overlay_spinner.props.visible = False
        dv.connecting_progress_bar.props.visible = False
