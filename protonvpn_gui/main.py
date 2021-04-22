import os
import sys

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gio, Gtk
from proton.constants import VERSION as proton_version
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.constants import APP_VERSION as lib_version

from .constants import APP_VERSION
from .logger import logger
from .model.utilities import Utilities
from .model.background_process import BackgroundProcess
from .view.dashboard import DashboardView
from .view.login import LoginView
from .view_model.dashboard import DashboardViewModel
from .view_model.login import LoginViewModel
from .model.server_list import ServerList
from .model.country_item import CountryItem
from .view.dialog import QuitDialog, LogoutDialog, AboutDialog


class ProtonVPNGUI(Gtk.Application):
    """ProtonVPN GTK Applcation.

    Windows are composite objects. Follows
    MVVM pattern.
    """
    def __init__(self):
        super().__init__(
            application_id='com.protonvpn.www',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_startup(self):
        """Default GTK method.

        Runs at application startup, to load
        any necessary UI elements.
        """
        logger.info(
            "\n"
            + "---------------------"
            + "----------------"
            + "------------\n\n"
            + "-----------\t"
            + "Initialized protonvpn"
            + "\t-----------\n\n"
            + "---------------------"
            + "----------------"
            + "------------"
        )
        logger.info(
            "ProtonVPN v{} "
            "(protonvpn-nm-lib v{}; proton-client v{})".format(
                APP_VERSION, lib_version, proton_version
            )
        )
        if "SUDO_UID" in os.environ:
            logger.info("Initialized app with sudo")
            print(
                "\nRunning ProtonVPN as root is not supported and "
                "is highly discouraged, as it might introduce "
                "undesirable side-effects."
            )
            user_input = input("Are you sure that you want to proceed (y/N): ")
            user_input = user_input.lower()
            if not user_input == "y":
                logger.info("Quit app as sudo")
                self.on_quit()

        Gtk.Application.do_startup(self)

        self.setup_actions()
        logger.info("Startup successful")

    def on_quit(self, *args):
        """On app quit event hanlder."""
        logger.info("Quit app")
        if protonvpn.get_active_protonvpn_connection():
            QuitDialog(self, self.quit_)
            return

        self.quit_()

    def quit_(self):
        protonvpn.disconnect()
        self.quit()

    def on_logout(self, *args):
        if protonvpn.get_active_protonvpn_connection():
            LogoutDialog(self, self.logout)
            return

        self.logout()

    def logout(self):
        active_windows = self.get_windows()
        protonvpn.logout()
        logger.info("Destroying all windows \"{}\"".format(active_windows))
        for win in active_windows:
            win.destroy()

        self.do_activate()

    def on_click_about(self, simple_action, _):
        AboutDialog(self)

    def on_display_preferences(self, *args):
        """On app display preferences event hanlder."""
        logger.info("Display preferences")
        print("To-do")

    def do_activate(self):
        """Default GTK method.

        Runs after app startup and before displaying any windows.
        """
        win = self.props.active_window

        if not win:
            if not protonvpn.check_session_exists():
                win = self.get_login_window()
            else:
                win = self.get_dashboard_window()

        logger.info("Window to display {}".format(win))
        win.present()

    def get_login_window(self):
        """Get login window.

        Returns:
            LoginView
        """
        login_view_model = LoginViewModel(
            BackgroundProcess
        )
        return LoginView(
            application=self,
            view_model=login_view_model,
            dashboard_window=self.get_dashboard_window
        )

    def get_dashboard_window(self):
        """Get dashboard window.

        Returns:
            DashboardView
        """
        server_list = ServerList(
            country_item=CountryItem
        )
        dashboard_view_model = DashboardViewModel(
            Utilities, BackgroundProcess, server_list
        )
        return DashboardView(
            application=self,
            view_model=dashboard_view_model
        )

    def setup_actions(self):
        quit_app = Gio.SimpleAction.new("quit", None)
        quit_app.connect("activate", self.on_quit)
        self.add_action(quit_app)

        logout = Gio.SimpleAction.new("logout", None)
        logout.connect("activate", self.on_logout)
        self.add_action(logout)

        about_dialog = Gio.SimpleAction.new("about", None)
        about_dialog.connect("activate", self.on_click_about)
        self.add_action(about_dialog)

        # TO-DO: Implement preferences
        # display_preferences = Gio.SimpleAction.new("display_preferences", None)
        # display_preferences.connect("activate", self.on_display_preferences)
        # self.add_action(display_preferences)


def main():
    app = ProtonVPNGUI()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
