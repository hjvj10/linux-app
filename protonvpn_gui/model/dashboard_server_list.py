from protonvpn_nm_lib import Country
from protonvpn_nm_lib import ServerList
from .country_item import CountryItem
from protonvpn_nm_lib.enums import UserTierEnum, ServerTierEnum


class DashboardServerList:
    """DashboardServerList class.

    This class holds the list of servers that are to be fed to the
    dashboardserver list. This class can either generate a list with
    secure core servers or a list with non-secure servers.

    Properties:
        server_list: list
            contains a list of CountryItem

    Methods:
        generate_server_list()
            generates the neccesary elements for server listing and
            stores them in server_list
        sort_countries_by_tier()
            sorts the provided country list by the provided user tier
        sort_countries_by_name()
            sorts the provided country list by a countrys name
    """
    __server_list: list = None

    def __init__(self, country_item=CountryItem):
        self.country_item = country_item

    @property
    def server_list(self):
        return self.__server_list

    def generate_server_list(
        self,
        only_secure_core=False,
        server_list=ServerList.load_servers_from_file()
    ):
        self.__server_list = []
        country_code_with_matching_servers = self\
            ._get_country_code_with_matching_servers(server_list)

        for country_code, servername_list in country_code_with_matching_servers.items(): # noqa
            country_item = self.country_item()
            country_item.entry_country_code = country_code

            if only_secure_core:
                country_item.create_secure_core_country(
                    servername_list, server_list
                )
            else:
                country_item.create_non_secure_core_country(
                    servername_list, server_list
                )

            self.__server_list.append(country_item)

    def _get_country_code_with_matching_servers(self, server_list):
        country = Country()
        return country\
            .get_dict_with_country_code_servername(
                server_list.servers
            )

    def sort_countries_by_tier(self, user_tier, connect_list):
        if user_tier == UserTierEnum.FREE:
            connect_list.sort(
                key=lambda country: any(
                    tier == ServerTierEnum.FREE
                    for tier
                    in country.tiers
                ),
                reverse=True
            )

    def sort_countries_by_name(self, connect_list):
        connect_list.sort(key=lambda country: country.country_name)
