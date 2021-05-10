import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")
gi.require_version("AppIndicator3", "0.1")
import os

from gi.repository import AppIndicator3 as appindicator
from gi.repository import GObject, Gtk, Notify
from ..constants import ICON_DIR_PATH, VPN_TRAY_ON, VPN_TRAY_OFF, VPN_TRAY_ERROR
from ..enums import IndicatorActionEnum
from ..rx.subject.replaysubject import ReplaySubject


class ProtonVPNIndicator:
    ON_PATH = os.path.join(ICON_DIR_PATH, VPN_TRAY_ON)
    OFF_PATH = os.path.join(ICON_DIR_PATH, VPN_TRAY_OFF)
    ERROR_PATH = os.path.join(ICON_DIR_PATH, VPN_TRAY_ERROR)

    def __init__(self, application):
        super().__init__()
        self.indicator_action = ReplaySubject(buffer_size=1)
        self.application = application
        self.gobject = GObject
        self.menu = self.menu()
        self.indicator = appindicator.Indicator.new(
            "ProtonVPN Indicator",
            "protonvpn-indicator",
            appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)

        self.tray_title = "ProtonVPN"
        self.notify = Notify
        self.notify.init("ProtonVPN Tray")
        self.indicator.set_icon_full(self.ERROR_PATH, "protonvpn")

    def menu(self):
        self.menu = Gtk.Menu()

        self.separator_0 = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator_0)
        self.separator_0.show()

        self.q_connect = Gtk.MenuItem(label="Quick Connect")
        self.q_connect.connect("activate", self.__quick_connect)
        self.menu.append(self.q_connect)
        self.q_connect.show()

        self.disconn = Gtk.MenuItem(label="Disconnect")
        self.disconn.connect("activate", self.__disconnect)
        self.menu.append(self.disconn)
        self.disconn.show()

        self.separator_1 = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator_1)
        self.separator_1.show()

        self.gui = Gtk.MenuItem(label="Show")
        self.gui.connect("activate", self.__show_gui)
        self.menu.append(self.gui)
        self.gui.show()

        self.separator_2 = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator_2)
        self.separator_2.show()

        self.exittray = Gtk.MenuItem(label="Quit")
        self.exittray.connect("activate", self.__quit_protonvpn)
        self.menu.append(self.exittray)
        self.exittray.show()

        return self.menu

    def __quick_connect(self, _):
        """Makes a quick connection by making a cli call to protonvpn-cli-ng"""
        self.indicator_action.on_next(IndicatorActionEnum.QUICK_CONNECT)

    def __disconnect(self, _):
        """__disconnects from a current vpn connection"""
        self.indicator_action.on_next(IndicatorActionEnum.DISCONNECT)

    def __show_gui(self, _):
        """Displays the GUI."""
        self.indicator_action.on_next(IndicatorActionEnum.SHOW_GUI)

    def __quit_protonvpn(self, _):
        """Quit/Stop the tray icon.
        """
        self.application.on_quit()
        pass

    def set_connected_state(self):
        self.indicator.set_icon_full(self.ON_PATH, "protonvpn")

    def set_disconnected_state(self):
        self.indicator.set_icon_full(self.OFF_PATH, "protonvpn")

    def set_error_state(self):
        self.indicator.set_icon_full(self.ERROR_PATH, "protonvpn")
