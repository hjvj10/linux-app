from protonvpn_nm_lib import exceptions
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import requests
from ..logger import logger


class DashboardService:

    def __init__(
        self,
        reconector_manager,
        user_conf_manager,
        ks_manager,
        connection_manager,
        user_manager,
        server_manager,
        ipv6_lp_manager,
        certificate_manager
    ):
        self.reconector_manager = reconector_manager
        self.user_conf_manager = user_conf_manager
        self.ks_manager = ks_manager
        self.connection_manager = connection_manager
        self.user_manager = user_manager
        self.server_manager = server_manager
        self.ipv6_lp_manager = ipv6_lp_manager
        self.certificate_manager = certificate_manager
        self.session = None
        self.CONNECT_DICT = {
            "servername": self.server_manager.get_config_for_specific_server,
            "fastest": self.server_manager.get_config_for_fastest_server,
            "random": self.server_manager.get_config_for_random_server,
            "country-code": self.server_manager.get_config_for_fastest_server_in_country, # noqa
            "secure-cpre": self.server_manager.get_config_for_fastest_server_with_specific_feature, # noqa
            "peer2peer": self.server_manager.get_config_for_fastest_server_with_specific_feature, # noqa
            "tor": self.server_manager.get_config_for_fastest_server_with_specific_feature, # noqa
        }

    def check_internet_connectivity(self):
        """Proxy method to connection manager:

        connection_manager.check_internet_connectivity()
        """
        logger.info("Check internet connectivity")
        conn_err = None
        try:
            self.connection_manager.check_internet_connectivity(
                self.user_conf_manager.killswitch
            )
        except (exceptions.ProtonVPNException, Exception) as e: # noqa
            logger.exception(e)
            conn_err = e

        return conn_err

    def get_active_proton_connection(self):
        """Proxy method to connection manager:

        connection_manager.get_proton_connection()
        """
        logger.info("Getting active protonvpn connection")
        try:
            resp = self.connection_manager.get_proton_connection(
                "active_connections"
            )
        except (
            exceptions.ProtonVPNException, dbus.DBusException, Exception
        ) as e:
            logger.exception(e)
            resp = False

        return resp[0]

    def get_ip(self):
        logger.info("Getting IP")
        try:
            r = requests.get("https://ip.me/")
            ip = r.text.strip()
        except (Exception, requests.exceptions.BaseHTTPError) as e:
            logger.exception(e)
            ip = "Unable to fetch IP"

        logger.info("IP fetched")
        return ip

    def prepare_fastest_connection(self):
        logger.info("Preparing fastest connection")
        try:
            conn_status = self.prepare_connection("fastest")
        except Exception as e:
            logger.exception(e)
            return e

        if isinstance(conn_status, str):
            return Exception(conn_status)

        logger.info("Fastest connection ready: {}".format(conn_status))
        return conn_status

    def prepare_connection(self, connection_type):
        try:
            self.set_session()
        except Exception as e:
            logger.exception(e)
            return e

        conn_status = self.setup_connection(connection_type)
        return conn_status

    def start_vpn_connection(self):
        logger.info("Starting vpn conection")
        self.connection_manager.start_connection()

    def setup_connection(self, connection_type):
        logger.info("Setting up vpn conection")
        ovpn_resp = self.get_ovpn_credentials()
        resp = self.get_connection_configurations(connection_type)

        if isinstance(resp, str):
            return resp

        if isinstance(resp, str):
            return ovpn_resp

        openvpn_username, openvpn_password = ovpn_resp[0], ovpn_resp[1]

        (
            servername, domain,
            server_feature,
            filtered_servers, servers
        ) = resp[0], resp[1], resp[2], resp[3], resp[4]

        (
            certificate_fp,
            matching_domain,
            entry_ip,
            server_label
        ) = self.server_manager.generate_server_certificate(
            servername, domain, server_feature,
            "tcp", servers, filtered_servers
        )

        print("Entry IP: ", entry_ip)

        if server_label is not None:
            openvpn_username = openvpn_username + "+b:" + server_label

        resp = self.add_vpn_connection(
            certificate_fp, openvpn_username, openvpn_password,
            matching_domain, entry_ip
        )

        if resp is not None:
            return resp

        conn_status = self.connection_manager.display_connection_status(
            "all_connections"
        )

        return conn_status

    def get_ovpn_credentials(self, retry=False):
        """Proxymethod to get user OVPN credentials."""
        logger.info("Getting ovpn credentials")

        openvpn_username, openvpn_password = None, None
        error = False

        try:
            if retry:
                self.user_manager.cache_user_data(self.session)
            openvpn_username, openvpn_password = self.user_manager.get_stored_vpn_credentials( # noqa
                self.session
            )
        except exceptions.JSONDataEmptyError as e:
            logger.exception(e)
            return "\nThe stored session might be corrupted. " \
                "Please, try to login again."
        except (
            exceptions.JSONDataError,
            exceptions.JSONDataNoneError
        ) as e:
            logger.exception(e)
            error = "cache_user_data"
        except exceptions.APITimeoutError as e:
            logger.exception(e)
            return "\nConnection timeout, unable to reach API."
        except exceptions.API10013Error as e:
            logger.exception(e)
            return "\nCurrent session is invalid, " \
                "please logout and login again."
        except exceptions.ProtonSessionWrapperError as e:
            logger.exception(e)
            return "\nUnknown API error occured: {}".format(e)
        except Exception as e:
            logger.exception(e)
            return "\nUnknown error occured: {}.".format(e)

        if error:
            return self.get_ovpn_credentials(1, True)

        return openvpn_username, openvpn_password

    def get_connection_configurations(self, connection_type, optional_arg=None): # noqa
        logger.info("Getting connection configurations")
        try:
            return self.CONNECT_DICT[connection_type](
                self.session,
                optional_arg
            )
        except (
            exceptions.JSONDataEmptyError,
            exceptions.JSONDataError,
            exceptions.JSONDataNoneError
        ) as e:
            logger.exception(e)
            return "\nThe stored session might be corrupted. " \
                "Please, try to login again."
        except (KeyError, TypeError, ValueError) as e:
            logger.exception(e)
            return "\nError: {}".format(e)
        except exceptions.EmptyServerListError as e:
            logger.exception(e)
            return "\n{} This could mean that the " \
                "server(s) are under maintenance or " \
                "inaccessible with your plan.".format(e)
        except exceptions.IllegalServername as e:
            logger.exception(e)
            return "\nIllegalServername: {}".format(e)
        except exceptions.CacheLogicalServersError as e:
            logger.exception(e)
            return "\nCacheLogicalServersError: {}".format(e)
        except exceptions.MissingCacheError as e:
            logger.exception(e)
            return "\nMissingCacheError: {}".format(e)
        except exceptions.API403Error as e:
            logger.exception(e)
            return "\nAPI403Error: {}".format(e.error)
        except exceptions.API10013Error as e:
            logger.exception(e)
            return "\nCurrent session is invalid, " \
                "please logout and login again."
        except exceptions.APITimeoutError as e:
            logger.exception(e)
            return "\nConnection timeout, unable to reach API."
        except exceptions.ProtonSessionWrapperError as e:
            logger.exception(e)
            return "\nUnknown API error occured: {}".format(e.error)
        except Exception as e:
            logger.exception(e)
            return "\nUnknown error occured: {}.".format(e)

    def add_vpn_connection(
        self, certificate_filename, openvpn_username,
        openvpn_password, domain, entry_ip
    ):
        """Proxymethod to add ProtonVPN connection."""
        logger.info("Adding vpn connection")
        try:
            self.connection_manager.add_connection(
                certificate_filename, openvpn_username, openvpn_password,
                self.certificate_manager.delete_cached_certificate, domain,
                self.user_conf_manager, self.ks_manager, self.ipv6_lp_manager,
                entry_ip
            )
            logger.info("VPN Connection added")
        except exceptions.ImportConnectionError as e:
            logger.exception(e)
            return "An error occured upon importing connection: "
        except Exception as e:
            logger.exception(e)
            return "Unknown error: {}".format(e)

        return None

    def set_session(self):
        """Proxymethod to get user session."""
        logger.info("Setting session")
        self.session = None

        try:
            self.session = self.user_manager.load_session()
        except exceptions.JSONDataEmptyError as e:
            logger.exception(e)
            raise Exception(
                "The stored session might be corrupted. "
                "Please, try to login again."
            )
        except (
            exceptions.JSONDataError,
            exceptions.JSONDataNoneError
        ) as e:
            logger.exception(e)
            raise Exception(
                "\nThere is no stored session. Please, login first."
            )
        except exceptions.AccessKeyringError as e:
            logger.exception(e)
            raise Exception(
                "Unable to load session. Could not access keyring."
            )
        except exceptions.KeyringError as e:
            logger.exception(e)
            raise Exception("\nUnknown keyring error occured: {}".format(e))
        except Exception as e:
            logger.exception(e)
            raise Exception("Unknown error occured: {}.".format(e))
