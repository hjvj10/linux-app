from protonvpn_nm_lib.enums import ServerTierEnum, FeatureEnum
import copy


class NoneSecureCoreServers:

    def __init__(self, user_tier):
        self.__servers = []
        self.__user_tier = user_tier

    @property
    def user_tier(self):
        return self.__user_tier

    @property
    def servers(self):
        return self.__servers

    @property
    def total_countries_count(self):
        return len(self.__servers) - self.internal_countries_count

    @property
    def free_countries_count(self):
        num_countries = 0
        for server in self.__servers:
            if ServerTierEnum.FREE == server.minimum_country_tier:
                num_countries += 1

        return num_countries

    @property
    def basic_countries_count(self):
        num_countries = 0
        for server in self.__servers:
            if ServerTierEnum.BASIC == server.minimum_country_tier:
                num_countries += 1

        return num_countries

    @property
    def plus_countries_count(self):
        num_countries = 0
        for server in self.__servers:
            if ServerTierEnum.PLUS_VISIONARY == server.minimum_country_tier:
                num_countries += 1

        return num_countries

    @property
    def internal_countries_count(self):
        num_countries = 0
        for server in self.__servers:
            if ServerTierEnum.PM == server.minimum_country_tier:
                num_countries += 1

        return num_countries

    def generate(self, unfiltered_server_list):
        self.__servers = []
        for country_item in unfiltered_server_list:
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

            copy_country_item.servers = self.__default_sort(
                copy_country_item
            )
            self.__servers.append(copy_country_item)

        sort_methods_by_tier = {
            ServerTierEnum.FREE: self.__sort_for_free_user,
            ServerTierEnum.BASIC: self.__sort_for_basic_user,
            ServerTierEnum.PLUS_VISIONARY: self.__sort_for_plus_user,
            ServerTierEnum.PM: self.__sort_for_internal_user,
        }

        try:
            sort_methods_by_tier[self.__user_tier]()
        except KeyError:
            self.__sort_for_free_users()

    def __default_sort(self, country_item):
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

    def __sort_for_free_user(self):
        free_countries = list(filter(
            lambda country: country.minimum_country_tier == ServerTierEnum.FREE,
            self.__servers
        ))
        upgrade_countries = list(filter(
            lambda country: country.minimum_country_tier != ServerTierEnum.FREE,
            self.__servers
        ))
        free_countries.sort(key=lambda country: country.country_name)
        upgrade_countries.sort(key=lambda country: country.country_name)
        free_countries.extend(upgrade_countries)
        self.__servers = free_countries

    def __sort_for_basic_user(self):
        free_and_basic_countries = list(filter(
            lambda country: country.minimum_country_tier.value <= ServerTierEnum.BASIC.value,
            self.__servers
        ))
        upgrade_countries = list(filter(
            lambda country: country.minimum_country_tier.value > ServerTierEnum.BASIC.value,
            self.__servers
        ))
        free_and_basic_countries.sort(key=lambda country: country.country_name)
        upgrade_countries.sort(key=lambda country: country.country_name)
        free_and_basic_countries.extend(upgrade_countries)
        self.__servers = free_and_basic_countries

    def __sort_for_plus_user(self):
        self.__servers.sort(
            key=lambda country: country.country_name
        )

    def __sort_for_internal_user(self):
        internal_servers = list(filter(
            lambda country: country.minimum_country_tier == ServerTierEnum.PM,
            self.__servers
        ))
        other_servers = list(filter(
            lambda country: country.minimum_country_tier != ServerTierEnum.PM,
            self.__servers
        ))
        internal_servers.sort(key=lambda country: country.country_name)
        other_servers.sort(key=lambda country: country.country_name)
        internal_servers.extend(other_servers)
        self.__servers = internal_servers
