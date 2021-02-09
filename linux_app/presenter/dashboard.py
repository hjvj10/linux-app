from protonvpn_nm_lib import exceptions


class DashboardPresenter:

    def __init__(self, 
        reconector_manager,
        user_conf_manager,
        ks_manager,
        connection_manager,
        user_manager,
        server_manager,
        ipv6_lp_manager
    ):
        self.reconector_manager = reconector_manager
        self.user_conf_manager =user_conf_manager
        self.ks_manager = ks_manager
        self.connection_manager = connection_manager
        self.user_manager = user_manager
        self.server_manager = server_manager
        self.ipv6_lp_manager = ipv6_lp_manager

        self.dashboard_view = None