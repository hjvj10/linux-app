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
        self.__remove_pressed_style(self.get_relative_to())

    def display_secure_core_settings(self, gio_action, _, button):
        self.title_label.content = "Secure-Core"
        self.description_label.content = "Route your most sensitive data " \
            "through our safest servers in privacy-friendly countries. " \
            "<LinkButton>Learn more."
        self.footnote.content = "Secure Core may reduce VPN speed"
        self.footnote.show = True

        child_widget = self.buttons_holder.get_child_at()
        # isinstance() was not picking up the types, so had to use ==
        if type(child_widget) == type(self.content_grid.widget):
            if not child_widget == self.secure_core_buttons_grid.widget:
                self.buttons_holder.remove_row(0)
                self.buttons_holder.attach(self.secure_core_buttons_grid.widget)
        else:
            self.buttons_holder.attach(self.secure_core_buttons_grid.widget)

        self.set_relative_to(button)
        self.__add_pressed_style(button)
        self.popup()

    def display_netshield_settings(self, gio_action, _, button):
        self.title_label.content = "Netshield"
        self.description_label.content = "Browse the Internet without ads " \
            "and malware. <LinkButton>Learn more."
        self.footnote.content = "If websites don't load, try " \
            "disabling Netshield"
        self.footnote.show = True

        child_widget = self.buttons_holder.get_child_at()
        # isinstance() was not picking up the types, so had to use ==
        if type(child_widget) == type(self.content_grid.widget):
            if not child_widget == self.netshield_buttons_grid.widget:
                self.buttons_holder.remove_row(0)
                self.buttons_holder.attach(self.netshield_buttons_grid.widget)
        else:
            self.buttons_holder.attach(self.netshield_buttons_grid.widget)

        self.set_relative_to(button)
        self.popup()
        self.__add_pressed_style(button)

    def display_killswitch_settings(self, gio_action, _, button):
        self.title_label.content = "Kill Switch"
        self.description_label.content = "Disables Internet if the VPN " \
            "connection drops to prevent accidental IP leak. "\
            "<LinkButton>Learn more."
        self.footnote.show = False

        child_widget = self.buttons_holder.get_child_at()
        # isinstance() was not picking up the types, so had to use ==
        if type(child_widget) == type(self.content_grid.widget):
            if not child_widget == self.killswitch_buttons_grid.widget:
                self.buttons_holder.remove_row(0)
                self.buttons_holder.attach(self.killswitch_buttons_grid.widget)
        else:
            self.buttons_holder.attach(self.killswitch_buttons_grid.widget)

        self.set_relative_to(button)
        self.popup()
        self.__add_pressed_style(button)

    def __create_widgets(self):
        self.content_grid = WidgetFactory.grid("container")
        self.title_label = WidgetFactory.label("quick_settings_title")
        self.description_label = WidgetFactory.label("quick_settings_description") # noqa
        self.buttons_holder = WidgetFactory.grid("buttons")
        self.buttons_holder.add_class("margin-bottom-20px")
        self.upgrade_button = WidgetFactory.button("dialog_upgrade")
        self.footnote = WidgetFactory.label("quick_settings_footnote")
        self.__create_secure_core_buttons()
        self.__create_netshield_buttons()
        self.__create_killswitch_buttons()

    def __attach_widgets_to_grid(self):
        self.content_grid.attach(self.title_label.widget)
        self.content_grid.attach_bottom_next_to(
            self.description_label.widget, self.title_label.widget
        )
        self.content_grid.attach_bottom_next_to(
            self.buttons_holder.widget, self.description_label.widget
        )
        self.content_grid.attach_bottom_next_to(
            self.upgrade_button.widget, self.buttons_holder.widget
        )
        self.content_grid.attach_bottom_next_to(
            self.footnote.widget, self.upgrade_button.widget
        )

    def __create_secure_core_buttons(self):
        self.secure_core_buttons_grid = WidgetFactory.grid("buttons")
        self.secure_core_buttons_grid.row_spacing = 15
        self.secure_core_button_off = SecureCoreOff()
        self.secure_core_button_on = SecureCoreOn()
        self.secure_core_buttons_grid.attach(
            self.secure_core_button_off.widget
        )
        self.secure_core_buttons_grid.attach_bottom_next_to(
            self.secure_core_button_on.widget,
            self.secure_core_button_off.widget
        )

    def __create_netshield_buttons(self):
        self.netshield_buttons_grid = WidgetFactory.grid("buttons")
        self.netshield_buttons_grid.row_spacing = 15
        self.netshield_button_off = NetshieldOff()
        self.netshield_button_malware = NetshieldMalware()
        self.netshield_button_ads_malware = NetshieldAdsMalware()

        self.netshield_buttons_grid.attach(self.netshield_button_off.widget)
        self.netshield_buttons_grid.attach_bottom_next_to(
            self.netshield_button_malware.widget,
            self.netshield_button_off.widget
        )
        self.netshield_buttons_grid.attach_bottom_next_to(
            self.netshield_button_ads_malware.widget,
            self.netshield_button_malware.widget
        )

    def __create_killswitch_buttons(self):
        self.killswitch_buttons_grid = WidgetFactory.grid("buttons")
        self.killswitch_buttons_grid.row_spacing = 15
        self.killswitch_button_off = KillSwitchOff()
        self.killswitch_button_on = KillSwitchOn()
        self.killswitch_button_alway_on = KillSwitchAlwaysOn()

        self.killswitch_buttons_grid.attach(self.killswitch_button_off.widget)
        self.killswitch_buttons_grid.attach_bottom_next_to(
            self.killswitch_button_on.widget,
            self.killswitch_button_off.widget
        )
        self.killswitch_buttons_grid.attach_bottom_next_to(
            self.killswitch_button_alway_on.widget,
            self.killswitch_button_on.widget,
        )

    def __add_pressed_style(self, button):
        button_context = button.get_style_context()
        button_context.add_class("pressed")

    def __remove_pressed_style(self, button):
        button_context = button.get_style_context()
        button_context.remove_class("pressed")


class QuickSettingButton:
    def __init__(self, img_factory_name, text, display_upgrade=False):
        self.__content = WidgetFactory.grid("buttons")
        self.__content.row_spacing = 10
        self.__content.column_spacing = 10
        self.__button = WidgetFactory.button("quick_setting")
        self.__img = WidgetFactory.image(img_factory_name)
        self.__label = WidgetFactory.label("quick_settings_button", text)
        self.display_upgrade = display_upgrade
        self.__button.custom_content(self.__content.widget)
        self.build()

    @property
    def widget(self):
        return self.__button.widget

    @property
    def text(self):
        return self.__label.content

    @text.setter
    def text(self, newvalue):
        self.__label.content = newvalue

    @property
    def img(self):
        return self.__img

    def build(self):
        self.__label.add_class("default-text-color")
        self.__content.attach(self.__img.widget)
        self.__content.attach_right_next_to(
            self.__label.widget, self.__img.widget
        )


class SecureCoreOff(QuickSettingButton):
    def __init__(self):
        super().__init__(
            "secure_cure_off",
            "Secure Cure Off"
        )


class SecureCoreOn(QuickSettingButton):
    def __init__(self):
        super().__init__(
            "secure_cure_on",
            "Secure Cure On"
        )


class NetshieldOff(QuickSettingButton):
    def __init__(self):
        super().__init__(
            "netshield_off",
            "Don't block"
        )


class NetshieldMalware(QuickSettingButton):
    def __init__(self):
        super().__init__(
            "netshield_malware",
            "Block malware only"
        )


class NetshieldAdsMalware(QuickSettingButton):
    def __init__(self):
        super().__init__(
            "netshield_ads_malware",
            "Block malware, ads & trackers"
        )


class KillSwitchOff(QuickSettingButton):
    def __init__(self):
        super().__init__(
            "killswitch_off",
            "Kill Switch Off"
        )


class KillSwitchOn(QuickSettingButton):
    def __init__(self):
        super().__init__(
            "killswitch_on",
            "Kill Switch On"
        )


class KillSwitchAlwaysOn(QuickSettingButton):
    def __init__(self):
        super().__init__(
            "killswitch_always_on",
            "Kill Switch Always-On"
        )
