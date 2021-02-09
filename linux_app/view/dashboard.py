import os

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, GdkPixbuf, Gio, Gtk

from ..constants import CSS_DIR_PATH, ICON_DIR_PATH, IMG_DIR_PATH, UI_DIR_PATH
from ..presenter.login import LoginPresenter
import threading

@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "dashboard.ui"))
class DashboardView(Gtk.ApplicationWindow):
    __gtype_name__ = 'DashboardView'

    # proton_username_entry = Gtk.Template.Child()
    icon_width = 18
    icon_heigt = 18

    def __init__(self, **kwargs):
        self.dashboard_presenter = kwargs.pop("presenter")
        super().__init__(**kwargs)
        self.setup_images()
        self.setup_css()
        self.setup_actions()

        self.dashboard_presenter.dashboard_view = self

    def setup_images(self):
        pass

    def setup_css(self):
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(os.path.join(CSS_DIR_PATH, "dashboard.css"))
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def setup_actions(self):
        pass

