from protonvpn_nm_lib.api import protonvpn
from .none_secure_core_servers import NoneSecureCoreServers
from .secure_core_servers import SecureCoreServers


class ServerList:
    """DashboardServerList class.

    This class holds the list of servers that are to be fed to the
    dashboardserver list. This class can either generate a list with
    secure core servers or a list with non-secure servers.

    Properties:
        server_list: list
            contains a list of CountryItem

    Methods:
        generate_list()
            generates the neccesary elements for server listing and
            stores them in server_list
    """
    def __init__(self, country_item):
        self.country_item = country_item

    @property
    def none_secure_core(self):
        return self.__none_secure_core_servers

    @property
    def secure_core(self):
        return self.__secure_core_servers

    def generate_list(self, user_tier):
        """Generate server list.

        Args:
            user_tier (ServerTierEnum)
        """
        unfiltered_server_list = []
        user_tier = user_tier
        server_list = protonvpn.get_session().servers
        server_filter = protonvpn.get_session().servers.filter
        country_code_with_matching_servers = self\
            .__get_country_code_with_matching_servers(server_list)

        self.__none_secure_core_servers = NoneSecureCoreServers(user_tier)
        self.__secure_core_servers = SecureCoreServers(user_tier)

        for country_code, servername_list in country_code_with_matching_servers.items(): # noqa
            country_item = self.country_item(server_filter, user_tier)
            country_item.entry_country_code = country_code

            country_item.create(servername_list)

            unfiltered_server_list.append(country_item)

        self.__none_secure_core_servers.generate(unfiltered_server_list)
        self.__secure_core_servers.generate(unfiltered_server_list)

    def __get_country_code_with_matching_servers(self, server_list):
        country = protonvpn.get_country()
        return country\
            .get_dict_with_country_code_servername(
                server_list
            )
