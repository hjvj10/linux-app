import os

import gi

gi.require_version('Gtk', '3.0')

import threading

from gi.repository import Gdk, GdkPixbuf, Gtk, Gio

from ..constants import CSS_DIR_PATH, ICON_DIR_PATH, UI_DIR_PATH, IMG_DIR_PATH
from ..enums import DashboardConnectionInfo


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "dashboard.ui"))
class DashboardView(Gtk.ApplicationWindow):
    __gtype_name__ = 'DashboardView'

    # Objects
    headerbar = Gtk.Template.Child()
    headerbar_menu_button = Gtk.Template.Child()
    dashboard_popover_menu = Gtk.Template.Child()
    overlay_spinner = Gtk.Template.Child()

    # Labels
    country_servername_label = Gtk.Template.Child()
    ip_label = Gtk.Template.Child()
    serverload_label = Gtk.Template.Child()
    download_speed_label = Gtk.Template.Child()
    upload_speed_label = Gtk.Template.Child()

    # Images/Icons
    headerbar_sign_icon = Gtk.Template.Child()
    overlay_logo_image = Gtk.Template.Child()
    server_load_image = Gtk.Template.Child()
    download_speed_image = Gtk.Template.Child()
    upload_speed_image = Gtk.Template.Child()

    # Grids
    connected_label_grid = Gtk.Template.Child()
    ip_label_grid = Gtk.Template.Child()
    ip_server_load_labels_grid = Gtk.Template.Child()
    connection_speed_label_grid = Gtk.Template.Child()

    # Boxes
    overlay_box = Gtk.Template.Child()

    # Constants
    icon_width = 40
    icon_heigt = 40

    def __init__(self, **kwargs):
        self.dashboard_presenter = kwargs.pop("presenter")
        super().__init__(**kwargs)

        self.dashboard_presenter.dashboard_view = self
        self.SET_UI_NOT_PROTECTED = {
            "property": "visible",
            "objects": [
                (self.download_speed_label, False),
                (self.download_speed_image, False),
                (self.upload_speed_image, False),
                (self.upload_speed_label, False),
                (self.serverload_label, False),
                (self.server_load_image, False),
                (self.overlay_box, False)
            ]
        }

        self.setup_images()
        self.setup_css()
        self.setup_actions()
        self.setup_loading_screen()

    def setup_loading_screen(self):
        self.overlay_spinner.set_property("width-request", 200)
        self.overlay_spinner.set_property("height-request", 200)
        self.overlay_spinner.start()

        self.overlay_box.set_property("visible", True)
        thread = threading.Thread(target=self.dashboard_presenter.init_check)
        thread.daemon = True
        thread.start()

    def connect_not_active(self, dashboard_connection_info):
        self.country_servername_label.set_text(
            dashboard_connection_info[
                DashboardConnectionInfo.COUNTRY_SERVERNAME_LABEL
            ]
        )
        ctx = self.country_servername_label.get_style_context()
        ctx.add_class("warning-color")
        self.ip_label.set_text(
            dashboard_connection_info[
                DashboardConnectionInfo.IP_LABEL
            ]
        )
        self.gtk_property_setter(self.SET_UI_NOT_PROTECTED)
        return False

    def gtk_property_setter(self, *args):
        for property_group in args:
            property = property_group.get("property")
            objects = property_group.get("objects")
            for object in objects:
                gtk_object, value = object
                gtk_object.set_property(property, value)

    def on_display_popover(self, gio_simple_action, _):
        self.dashboard_popover_menu.popup()

    def setup_images(self):
        protonvpn_headerbar_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale( # noqa
            filename=os.path.join(
                ICON_DIR_PATH,
                "protonvpn-sign-green.svg",

            ),
            width=self.icon_width,
            height=self.icon_heigt,
            preserve_aspect_ratio=True
        )
        logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(
                IMG_DIR_PATH,
                "protonvpn-logo-white.svg"
            ),
            width=325,
            height=250,
            preserve_aspect_ratio=True
        )

        self.headerbar_sign_icon.set_from_pixbuf(protonvpn_headerbar_pixbuf)
        self.overlay_logo_image.set_from_pixbuf(logo_pixbuf)

    def setup_css(self):
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
        # create action
        headerbar_menu = Gio.SimpleAction.new("show_menu", None)

        # connect action to callback
        headerbar_menu.connect("activate", self.on_display_popover)

        # add action
        self.add_action(headerbar_menu)
