from gi.repository import GLib
from protonvpn_nm_lib import exceptions


class LoginPresenter:

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

        self.login_view = None

    def login(self):
        username = self.login_view.proton_username_entry.get_text()
        password = self.login_view.proton_password_entry.get_text()

        result = None
        try:
            self.user_manager.login(username, password)
        except (TypeError, ValueError) as e:
            result = "Unable to authenticate: {}.".format(e)
        except (exceptions.API8002Error, exceptions.API85032Error) as e:
            result = "{}".format(e)
        except exceptions.APITimeoutError:
            result = "Connection timeout, unable to reach API."
        except (exceptions.UnhandledAPIError, exceptions.APIError) as e:
            result = "Unhandled API error occured: {}".format(e)
        except exceptions.ProtonSessionWrapperError as e:
            result = "Unknown API error occured: {}.".format(e)
        except (exceptions.ProtonVPNException, Exception) as e:
            # logger.exception(
            #     "[!] Unknown error: {}".format(e)
            # )
            result = "Unknown error occured: {}.".format(e)

        GLib.idle_add(self.login_view.update_login_status, result)
