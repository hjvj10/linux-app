import threading

from gi.repository import GLib

from ..constants import DASHBOARD_CONNECTION_INFO
from ..enums import DashboardConnectionInfo


class DashboardPresenter:

    def __init__(self, dasboard_service):
        self.dasboard_service = dasboard_service
        self.dashboard_view = None

    def on_startup(self, callback):
        thread = threading.Thread(
            target=self.init_check, args=[callback]
        )
        thread.daemon = True
        thread.start()

    def init_check(self, callback):
        conn_err = self.dasboard_service.check_internet_connectivity()

        if conn_err is not None:
            GLib.idle_add(self.dashboard_view.test_callbacv, conn_err)

        connection_exists = self.dasboard_service.get_active_proton_connection() # noqa

        if not connection_exists:
            ip = self.dasboard_service.get_ip()
            DASHBOARD_CONNECTION_INFO[
                DashboardConnectionInfo.COUNTRY_SERVERNAME_LABEL
            ] = "You are not connected"
            DASHBOARD_CONNECTION_INFO[
                DashboardConnectionInfo.IP_LABEL
            ] = ip

            GLib.idle_add(callback, DASHBOARD_CONNECTION_INFO)
            # start thrad to listen to NM vpn connection changes

        # fetch from connection

    def quick_connect(self):
        thread = threading.Thread(target=self.test)
        thread.daemon = True
        thread.start()

    def test(self):
        response = self.dasboard_service.connect_to_fastest_server()
        if response is None:
            print("All ok")
