import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
import os

from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk
from ..constants import ICON_DIR_PATH, VPN_TRAY_ON, VPN_TRAY_OFF, VPN_TRAY_ERROR
from ..enums import IndicatorActionEnum
from ..rx.subject.replaysubject import ReplaySubject
from ..logger import logger


class ProtonVPNIndicator:
    ON_PATH = os.path.join(ICON_DIR_PATH, VPN_TRAY_ON)
    OFF_PATH = os.path.join(ICON_DIR_PATH, VPN_TRAY_OFF)
    ERROR_PATH = os.path.join(ICON_DIR_PATH, VPN_TRAY_ERROR)

    def __init__(self, application):
        super().__init__()
        self.setup_reply_subject()
        self.__application = application
        self.__generate_menu()
        self.__indicator = appindicator.Indicator.new(
            "ProtonVPN Tray",
            "protonvpn-tray",
            appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.__indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.__indicator.set_menu(self.menu)

        self.__indicator.set_icon_full(self.OFF_PATH, "protonvpn")

    @property
    def application(self):
        return self.__application

    @property
    def indicator(self):
        return self.__indicator

    @property
    def login_action(self):
        return self.__indicator_login_action

    @property
    def dashboard_action(self):
        return self.__indicator_dashboard_action

    def __generate_menu(self):
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
        self.on_next_reply(IndicatorActionEnum.QUICK_CONNECT)

    def __disconnect(self, _):
        """__disconnects from a current vpn connection"""
        self.on_next_reply(IndicatorActionEnum.DISCONNECT)

    def __show_gui(self, _):
        """Displays the GUI."""
        self.on_next_reply(IndicatorActionEnum.SHOW_GUI)

    def __quit_protonvpn(self, _):
        """Quit/Stop the tray icon.
        """
        self.__application.on_quit()

    def on_next_reply(self, indicator_enum):
        from protonvpn_gui.rx.internal.exceptions import DisposedException
        try:
            self.__indicator_dashboard_action.on_next(indicator_enum)
        except DisposedException:
            pass
        except Exception as e:
            logger.exception(e)

        try:
            self.__indicator_login_action.on_next(indicator_enum)
        except DisposedException:
            pass
        except Exception as e:
            logger.exception(e)

    def set_connected_state(self):
        self.__indicator.set_icon_full(self.ON_PATH, "protonvpn")

    def set_disconnected_state(self):
        self.__indicator.set_icon_full(self.OFF_PATH, "protonvpn")

    def set_error_state(self):
        self.__indicator.set_icon_full(self.ERROR_PATH, "protonvpn")

    def setup_reply_subject(self):
        self.__indicator_login_action = ReplaySubject(buffer_size=1)
        self.__indicator_dashboard_action = ReplaySubject(buffer_size=1)
