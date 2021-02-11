import os
import sys

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gio, Gtk
from protonvpn_nm_lib.services.certificate_manager import CertificateManager
from protonvpn_nm_lib.services.connection_manager import ConnectionManager
from protonvpn_nm_lib.services.ipv6_leak_protection_manager import \
    IPv6LeakProtectionManager
from protonvpn_nm_lib.services.killswitch_manager import KillSwitchManager
from protonvpn_nm_lib.services.reconnector_manager import ReconnectorManager
from protonvpn_nm_lib.services.server_manager import ServerManager
from protonvpn_nm_lib.services.user_configuration_manager import \
    UserConfigurationManager
from protonvpn_nm_lib.services.user_manager import UserManager

from linux_app.presenter.login import LoginPresenter
from linux_app.presenter.dashboard import DashboardPresenter

from linux_app.view.login import LoginView
from linux_app.view.dashboard import DashboardView


class ProtonVPNLogin(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id='com.protonvpn.www',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.reconector_manager = ReconnectorManager()
        self.user_conf_manager = UserConfigurationManager()
        self.ks_manager = KillSwitchManager(self.user_conf_manager)
        self.connection_manager = ConnectionManager()
        self.user_manager = UserManager(self.user_conf_manager)
        self.server_manager = ServerManager(
            CertificateManager(), self.user_manager
        )
        self.ipv6_lp_manager = IPv6LeakProtectionManager()

    def do_activate(self):
        # win = self.props.active_window

        # if not win:
        return self.get_login_window

        # win.present()

    def get_login_window(self):
        login_presenter = LoginPresenter(
            self.reconector_manager,
            self.user_conf_manager,
            self.ks_manager,
            self.connection_manager,
            self.user_manager,
            self.server_manager,
            self.ipv6_lp_manager
        )
        return LoginView(
            application=self,
            presenter=login_presenter,
            dashboard_window=self.get_dashboard_window()
        )

    def get_dashboard_window(self):
        dashboard_presenter = DashboardPresenter(
            self.reconector_manager,
            self.user_conf_manager,
            self.ks_manager,
            self.connection_manager,
            self.user_manager,
            self.server_manager,
            self.ipv6_lp_manager
        )
        return DashboardView(
            application=self,
            presenter=dashboard_presenter
        )


def test_gtk():
    app = ProtonVPNLogin()
    print(app.get_login_window())
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


test_gtk()