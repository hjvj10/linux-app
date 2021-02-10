import os

import gi

gi.require_version('Gtk', '3.0')

import threading

from gi.repository import Gdk, GdkPixbuf, Gtk, Gio

from ..constants import CSS_DIR_PATH, ICON_DIR_PATH, UI_DIR_PATH, IMG_DIR_PATH


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "dashboard.ui"))
class DashboardView(Gtk.ApplicationWindow):
    __gtype_name__ = 'DashboardView'

    headerbar = Gtk.Template.Child()
    headerbar_image = Gtk.Template.Child()
    overlay_logo_image = Gtk.Template.Child()
    headerbar_menu_button = Gtk.Template.Child()
    dashboard_popover_menu = Gtk.Template.Child()

    # Grids
    connected_label_grid = Gtk.Template.Child()
    ip_label_grid = Gtk.Template.Child()
    ip_server_load_labels_grid = Gtk.Template.Child()
    connection_speed_label_grid = Gtk.Template.Child()

    # Labels
    country_servername_label = Gtk.Template.Child()
    ip_label = Gtk.Template.Child()
    serverload_label = Gtk.Template.Child()
    download_speed_label = Gtk.Template.Child()
    upload_speed_label = Gtk.Template.Child()

    icon_width = 50
    icon_heigt = 50

    def __init__(self, **kwargs):
        self.dashboard_presenter = kwargs.pop("presenter")
        super().__init__(**kwargs)
        self.setup_images()
        self.setup_css()
        self.setup_actions()
        # check for internet connectivty
        self.dashboard_presenter.dashboard_view = self
        # thread = threading.Thread(target=self.dashboard_presenter.init_check, args=(args, kwargs))
        # thread.daemon = True
        # thread.start()

    def on_menuitem_activated(self, *args):
        print(args)

    def setup_images(self):
        self.protonvpn_headerbar_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale( # noqa
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

    def on_display_popover(self, gio_simple_action, _):
        self.dashboard_popover_menu.popup()
