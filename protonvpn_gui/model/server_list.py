from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.enums import ServerTierEnum, FeatureEnum
import copy


class ServerList:
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

    def __init__(self, country_item):
        self.country_item = country_item
        self.__non_secure_core_servers = None
        self.__secure_core_servers = None
        self.__unfiltered_server_list = None
        self.__user_tier = None
        self.__display_secure_core_servers = False
        self.__default_list = None
        self.__num_free_countries = None
        self.__num_basic_countries = None
        self.__num_plus_countries = None

    @property
    def display_secure_core(self):
        return self.__display_secure_core_servers

    @display_secure_core.setter
    def display_secure_core(self, newvalue):
        self.__display_secure_core_servers = newvalue
        self.__copy_servers()

    @property
    def servers(self):
        if not self.__default_list:
            self.__copy_servers()

        return self.__default_list

    @property
    def user_tier(self):
        return self.__user_tier

    @property
    def ammount_of_free_countries(self):
        if self.__num_free_countries is None:
            self.__num_free_countries = 0
            for server in self.servers:
                if ServerTierEnum.FREE in server.tiers:
                    self.__num_free_countries += 1

        return self.__num_free_countries

    @property
    def ammount_of_basic_countries(self):
        if self.__num_basic_countries is None:
            self.__num_basic_countries = 0
            for server in self.servers:
                if ServerTierEnum.BASIC in server.tiers:
                    self.__num_basic_countries += 1

        return self.__num_basic_countries

    @property
    def ammount_of_plus_countries(self):
        if self.__num_plus_countries is None:
            self.__num_plus_countries = 0
            for server in self.servers:
                if ServerTierEnum.PLUS_VISIONARY in server.tiers:
                    self.__num_plus_countries += 1

        return self.__num_plus_countries

    @property
    def total_ammount_of_countries(self):
        return len(self.servers)

    def __copy_servers(self):
        if self.__display_secure_core_servers:
            self.__default_list = copy.deepcopy(
                self.__secure_core_servers
            )
        else:
            self.__default_list = copy.deepcopy(
                self.__non_secure_core_servers
            )

    def generate_list(self, user_tier):
        """Generate server list.

        Args:
            user_tier (ServerTierEnum)
            only_secure_core (bool)
        """
        self.__unfiltered_server_list = []
        self.__user_tier = user_tier
        server_list = protonvpn.get_session().servers
        country_code_with_matching_servers = self\
            .__get_country_code_with_matching_servers(server_list)

        for country_code, servername_list in country_code_with_matching_servers.items(): # noqa
            country_item = self.country_item()
            country_item.entry_country_code = country_code

            country_item.create(
                self.__user_tier, servername_list
            )
            self.__unfiltered_server_list.append(country_item)

        self.__generate_secure_core_list()
        self.__generate_non_secure_core_list()
        self.__num_free_countries = None
        self.__num_basic_countries = None
        self.__num_plus_countries = None

    def __get_country_code_with_matching_servers(self, server_list):
        country = protonvpn.get_country()
        return country\
            .get_dict_with_country_code_servername(
                server_list
            )

    def __generate_secure_core_list(self):
        self.__secure_core_servers = []
        for country_item in self.__unfiltered_server_list:
            copy_country_item = copy.deepcopy(country_item)
            copy_country_item.servers = list(filter(
                lambda server: any(
                    feature == FeatureEnum.SECURE_CORE
                    for feature
                    in server.features
                ), country_item.servers
            ))
            # Shallow copy as this is a one layer list
            features = copy.copy(country_item.features)
            for feature in features:
                if feature != FeatureEnum.SECURE_CORE:
                    try:
                        copy_country_item.features.pop(feature)
                    except IndexError:
                        pass

            self.__secure_core_servers.append(copy_country_item)

    def __generate_non_secure_core_list(self):
        self.__non_secure_core_servers = []
        for country_item in self.__unfiltered_server_list:
            copy_country_item = copy.deepcopy(country_item)
            copy_country_item.servers = list(filter(
                lambda server: all(
                    feature != FeatureEnum.SECURE_CORE
                    for feature
                    in server.features
                ), country_item.servers
            ))
            try:
                copy_country_item.features.pop(FeatureEnum.SECURE_CORE)
            except IndexError:
                pass

            copy_country_item.servers = self.__sort_non_secure_servers(
                copy_country_item
            )
            self.__non_secure_core_servers.append(copy_country_item)

        self.__sort_countries_by_tier()

    def __sort_countries_by_tier(self):
        if self.__user_tier == ServerTierEnum.FREE:
            self.__non_secure_core_servers.sort(
                key=lambda country: any(
                    tier == ServerTierEnum.FREE
                    for tier
                    in country.tiers
                ),
                reverse=True
            )

    def __sort_non_secure_servers(self, country_item):
        matching_server = list(filter(
            lambda server: server.tier == self.__user_tier,
            country_item.servers
        ))
        matching_server.sort(
            key=lambda server: server.name
        )
        non_matching_servers = list(filter(
            lambda server: server.tier != self.__user_tier,
            country_item.servers
        ))
        non_matching_servers.sort(
            key=lambda server: server.name
        )
        non_matching_servers.sort(
            key=lambda server: server.tier.value, reverse=True
        )
        matching_server.extend(
            non_matching_servers
        )

        return matching_server

    def sort_countries_by_name(self):
        if self.__user_tier != ServerTierEnum.FREE:
            try:
                self.__default_list.sort(
                    key=lambda country: country.country_name
                )
            except TypeError:
                pass
