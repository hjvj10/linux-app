from protonvpn_nm_lib import exceptions
import dbus
import requests


class DashboardService:

    def __init__(
        self,
        reconector_manager,
        user_conf_manager,
        ks_manager,
        connection_manager,
        user_manager,
        server_manager,
        ipv6_lp_manager
    ):
        self.reconector_manager = reconector_manager
        self.user_conf_manager = user_conf_manager
        self.ks_manager = ks_manager
        self.connection_manager = connection_manager
        self.user_manager = user_manager
        self.server_manager = server_manager
        self.ipv6_lp_manager = ipv6_lp_manager

    def check_internet_connectivity(self):
        """Proxy method to connection manager:

        connection_manager.check_internet_connectivity()
        """
        conn_err = None
        try:
            self.connection_manager.check_internet_connectivity(
                self.user_conf_manager.killswitch
            )
        except (exceptions.ProtonVPNException, Exception) as e: # noqa
            conn_err = e

        return conn_err

    def get_active_proton_connection(self):
        """Proxy method to connection manager:

        connection_manager.get_proton_connection()
        """
        try:
            resp = self.connection_manager.get_proton_connection(
                "active_connections"
            )
        except (
            exceptions.ProtonVPNException, dbus.DBusException, Exception
        ):
            resp = False

        return resp[0]

    def get_ip(self):
        try:
            r = requests.get("https://ip.me/")
            ip = r.text.strip()
        except (Exception, requests.exceptions.BaseHTTPError):
            ip = "Unable to fetch IP"

        return ip
