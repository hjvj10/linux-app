import os
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, Gtk
from protonvpn_nm_lib.api import protonvpn

from ..constants import (CSS_DIR_PATH, KILLSWITCH_ICON_SET, NETSHIELD_ICON_SET,
                         SECURE_CORE_ICON_SET, UI_DIR_PATH)
from ..enums import (DashboardKillSwitchIconEnum, DashboardNetshieldIconEnum,
                     DashboardSecureCoreIconEnum)
from ..factory.abstract_widget_factory import WidgetFactory


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "quick_settings_popover.ui"))
class QuickSettingsPopoverView(Gtk.Popover):
    """QuickSettings Popover view class. GTK Composite object."""
    __gtype_name__ = 'QuickSettingsPopoverView'

    quick_settings_popover_container_grid = Gtk.Template.Child()

    def __init__(self, dashboard_view_model):
        super().__init__()
        self.dashboard_view_model = dashboard_view_model

        self.__create_widgets()
        self.__attach_widgets_to_grid()
        self.quick_settings_popover_container_grid.attach(
            self.content_grid.widget, 0, 0, 1, 1
        )
        self.connect("closed", self.on_closed_popover)

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

    def on_closed_popover(self, gtk_popver):
        self.__remove_pressed_style(self.get_relative_to())

    def display_secure_core_settings(self, gio_action, _, button):
        self.title_label.content = "Secure-Core"
        self.description_label.content = "Route your most sensitive data " \
            "through our safest servers in privacy-friendly countries. " \
            "<LinkButton>Learn more."
        self.footnote.content = "Secure Core may reduce VPN speed"
        self.footnote.show = True

        self.__display_content_which_is_context_specific(
            self.secure_core_buttons_grid.widget
        )
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

        self.__display_content_which_is_context_specific(
            self.netshield_buttons_grid.widget
        )
        self.set_relative_to(button)
        self.popup()
        self.__add_pressed_style(button)

    def display_killswitch_settings(self, gio_action, _, button):
        self.title_label.content = "Kill Switch"
        self.description_label.content = "Disables Internet if the VPN " \
            "connection drops to prevent accidental IP leak. "\
            "<LinkButton>Learn more."
        self.footnote.show = False

        self.__display_content_which_is_context_specific(
            self.killswitch_buttons_grid.widget
        )
        self.set_relative_to(button)
        self.popup()
        self.__add_pressed_style(button)

    def __display_content_which_is_context_specific(self, resolve_for):
        """Displyes content which is based on which button is clicked.

        The argument that is passed is the one which is to be inserted
        into the popover since it contains the buttons that are context
        specific. If pressed on NetShield, then the netshield grid with
        buttons should be displayed.

        What this method does is check if the child of buttons_holder
        is a grid. If it is, then it means that there is another button grid
        being displayed. Thus is need to be first removed and then replaced
        with the resolved_for widget, which is the one that we want to display.

        Args:
            resolve_for (Gtk.Widget)
        """
        child_widget = self.buttons_holder.get_child_at()
        # isinstance() was not picking up the types, so had to use ==
        if type(child_widget) == type(self.content_grid.widget): # noqa
            if child_widget != resolve_for:
                self.buttons_holder.remove_row(0)
                self.buttons_holder.attach(resolve_for)
        else:
            self.buttons_holder.attach(resolve_for)

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
        self.secure_core_button_off = SecureCoreOff(self)
        self.secure_core_button_on = SecureCoreOn(self)
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
        self.netshield_button_off = NetshieldOff(self)
        self.netshield_button_malware = NetshieldMalware(self)
        self.netshield_button_ads_malware = NetshieldAdsMalware(self)

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
        self.killswitch_button_off = KillSwitchOff(self)
        self.killswitch_button_on = KillSwitchOn(self)
        self.killswitch_button_alway_on = KillSwitchAlwaysOn(self)

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

    icon_w = 25
    icon_h = 25
    selected_path = None
    available_path = None
    unavailable_path = None

    def __init__(self, popover_widget, img_factory_name, text):
        self.__popover_widget = popover_widget
        self.__content = WidgetFactory.grid("buttons")
        self.__content.row_spacing = 10
        self.__content.column_spacing = 10
        self.__button = WidgetFactory.button("quick_setting")
        self.__img = WidgetFactory.image(img_factory_name)
        self.__label = WidgetFactory.label("quick_settings_button", text)
        self.__upgrade_label = WidgetFactory.label(
            "quick_settings_upgrade_in_button", "UPGRADE"
        )
        self.__button.custom_content(self.__content.widget)
        self.build()

    def on_button_enter_notify(self, gtk_button, event_crossing):
        # TO-DO: Implement hand cursor when hovering
        # The line below shows how to create a new cursor object
        # cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        pass

    def on_button_leave_notify(self, gtk_button, event_crossing):
        # TO-DO: Implement hand cursor when hovering
        pass

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
        self.__content.attach(self.__img.widget)
        self.__content.attach_right_next_to(
            self.__label.widget, self.__img.widget
        )
        self.__content.attach_right_next_to(
            self.__upgrade_label.widget, self.__label.widget
        )

        self.__button.connect(
            "enter-notify-event", self.on_button_enter_notify
        )
        self.__button.connect(
            "leave-notify-event", self.on_button_leave_notify
        )

    def __selected(self, img_path=None):
        self.__label.replace_all_by("selected")
        self.__button.replace_all_by("selected")
        if not img_path:
            return
        self.__img.replace_with_new_icon(
            img_path, self.icon_w, self.icon_h
        )

    def __available(self, img_path=None):
        self.__label.replace_all_by("available")
        self.__button.replace_all_by("available")
        if not img_path:
            return
        self.__img.replace_with_new_icon(
            img_path, self.icon_w, self.icon_h
        )

    def __unavailable(self, img_path=None):
        self.__label.replace_all_by("unavailable")
        self.__button.replace_all_by("unavailable")
        if not img_path:
            return
        self.__img.replace_with_new_icon(
            img_path, self.icon_w, self.icon_h
        )

    def set_selected(self):
        if self.selected_path:
            self.__selected(
                self.selected_path
            )
        else:
            self.__selected()

    def set_available(self):
        if self.available_path:
            self.__available(
                self.available_path
            )
        else:
            self.__available()

    def set_unavailable(self):
        if self.unavailable_path:
            self.__unavailable(
                self.unavailable_path
            )
        else:
            self.__unavailable()

    @property
    def display_upgrade_label(self):
        return self.__upgrade_label.show

    @display_upgrade_label.setter
    def display_upgrade_label(self, newvalue):
        self.__upgrade_label.show = newvalue


class SecureCoreOff(QuickSettingButton):
    def __init__(self, popover_widget):
        super().__init__(
            popover_widget,
            "secure_cure_off",
            "Secure Cure Off"
        )
        self.display_upgrade_label = False
        self.set_selected()

    def set_unavailable(self):
        pass


class SecureCoreOn(QuickSettingButton):
    def __init__(self, popover_widget):
        super().__init__(
            popover_widget,
            "secure_cure_on",
            "Secure Cure On"
        )
        self.selected_path = SECURE_CORE_ICON_SET[DashboardSecureCoreIconEnum.ON_ACTIVE] # noqa
        self.available_path = SECURE_CORE_ICON_SET[DashboardSecureCoreIconEnum.ON_DEFAULT] # noqa
        self.unavailable_path = SECURE_CORE_ICON_SET[DashboardSecureCoreIconEnum.ON_DISABLE] # noqa
        self.set_available()


class NetshieldOff(QuickSettingButton):
    def __init__(self, popover_widget):
        super().__init__(
            popover_widget,
            "netshield_off",
            "Don't block"
        )
        self.display_upgrade_label = False
        self.set_selected()

    def set_unavailable(self):
        pass


class NetshieldMalware(QuickSettingButton):
    def __init__(self, popover_widget):
        super().__init__(
            popover_widget,
            "netshield_malware",
            "Block malware only"
        )
        self.selected_path = NETSHIELD_ICON_SET[DashboardNetshieldIconEnum.MALWARE_ACTIVE] # noqa
        self.available_path = NETSHIELD_ICON_SET[DashboardNetshieldIconEnum.MALWARE_DEFAULT] # noqa
        self.unavailable_path = NETSHIELD_ICON_SET[DashboardNetshieldIconEnum.MALWARE_DISABLE]  # noqa
        self.set_unavailable()


class NetshieldAdsMalware(QuickSettingButton):
    def __init__(self, popover_widget):
        super().__init__(
            popover_widget,
            "netshield_ads_malware",
            "Block malware, ads & trackers"
        )
        self.selected_path = NETSHIELD_ICON_SET[DashboardNetshieldIconEnum.MALWARE_ADS_ACTIVE] # noqa
        self.available_path = NETSHIELD_ICON_SET[DashboardNetshieldIconEnum.MALWARE_ADS_DEFAULT] # noqa
        self.unavailable_path = NETSHIELD_ICON_SET[DashboardNetshieldIconEnum.MALWARE_ADS_DISABLE]  # noqa
        self.set_unavailable()


class KillSwitchOff(QuickSettingButton):
    def __init__(self, popover_widget):
        super().__init__(
            popover_widget,
            "killswitch_off",
            "Kill Switch Off"
        )
        self.display_upgrade_label = False
        self.set_selected()

    def set_unavailable(self):
        pass


class KillSwitchOn(QuickSettingButton):
    def __init__(self, popover_widget):
        super().__init__(
            popover_widget,
            "killswitch_on",
            "Kill Switch On"
        )
        self.display_upgrade_label = False
        self.selected_path = KILLSWITCH_ICON_SET[DashboardKillSwitchIconEnum.ON_ACTIVE] # noqa
        self.available_path = KILLSWITCH_ICON_SET[DashboardKillSwitchIconEnum.ON_DEFAULT] # noqa
        self.unavailable_path = KILLSWITCH_ICON_SET[DashboardKillSwitchIconEnum.ON_DISABLE] # noqa
        self.set_available()


class KillSwitchAlwaysOn(QuickSettingButton):
    def __init__(self, popover_widget):
        super().__init__(
            popover_widget,
            "killswitch_always_on",
            "Kill Switch Always-On"
        )
        self.display_upgrade_label = False
        self.selected_path = KILLSWITCH_ICON_SET[DashboardKillSwitchIconEnum.ALWAYS_ON_ACTIVE] # noqa
        self.available_path = KILLSWITCH_ICON_SET[DashboardKillSwitchIconEnum.ALWAYS_ON_DEFAULT] # noqa
        self.unavailable_path = KILLSWITCH_ICON_SET[DashboardKillSwitchIconEnum.ALWAYS_ON_DISABLE] # noqa
        self.set_available()
