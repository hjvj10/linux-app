import os

import gi

gi.require_version('Gtk', '3.0')

from protonvpn_nm_lib.api import protonvpn
from gi.repository import Gdk, Gio, GLib, Gtk

from ..constants import (CSS_DIR_PATH, KILLSWITCH_ICON_SET, NETSHIELD_ICON_SET,
                         SECURE_CORE_ICON_SET, UI_DIR_PATH)
from ..factory.abstract_widget_factory import WidgetFactory


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "quick_settings_popover.ui"))
class QuickSettingsPopoverView(Gtk.Popover):
    """QuickSettings Popover view class. GTK Composite object."""
    __gtype_name__ = 'QuickSettingsPopoverView'

    quick_settings_popover_container_grid = Gtk.Template.Child()

    def __init__(self, dashboard_view_model):
        super().__init__()
        self.dashboard_view_model = dashboard_view_model

        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(
            os.path.join(CSS_DIR_PATH, "quick_settings_popover.css")
        )
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.__create_widgets()
        self.__attach_widgets_to_grid()
        self.quick_settings_popover_container_grid.attach(
            self.content_grid.widget, 0, 0, 1, 1
        )
        self.connect("closed", self.on_closed_popover)

    def on_closed_popover(self, gtk_popver):
        button_context = self.get_relative_to().get_style_context()
        button_context.remove_class("pressed")

    def display_secure_core_settings(self, gio_action, _, button):
        self.title_label.content = "Secure-Core"
        self.set_relative_to(button)
        self.show()
        self.__add_pressed_style(button)

    def display_netshield_settings(self, gio_action, _, button):
        self.title_label.content = "Netshield"
        self.set_relative_to(button)
        self.show()
        self.__add_pressed_style(button)

    def display_killswitch_settings(self, gio_action, _, button):
        self.title_label.content = "Kill Switch"
        self.set_relative_to(button)
        self.show()
        self.__add_pressed_style(button)

    def __create_widgets(self):
        self.content_grid = WidgetFactory.grid("quick_settings")
        self.title_label = WidgetFactory.label("quick_settings_title", "title")
        self.description_label = WidgetFactory.label(
            "quick_settings_description", "test"
        )
        self.buttons_grid = WidgetFactory.grid("quick_settings_buttons")
        self.footnote = WidgetFactory.label(
            "quick_settings_footnote", "footnote"
        )

    def __attach_widgets_to_grid(self):
        self.content_grid.attach(self.title_label.widget)
        self.content_grid.attach_bottom_next_to(
            self.description_label.widget, self.title_label.widget
        )
        self.content_grid.attach_bottom_next_to(
            self.buttons_grid.widget, self.description_label.widget
        )
        self.content_grid.attach_bottom_next_to(
            self.footnote.widget, self.buttons_grid.widget
        )

    def __attach_buttons_to_button_grid(self):
        pass

    def __add_pressed_style(self, button):
        button_context = button.get_style_context()
        button_context.add_class("pressed")
