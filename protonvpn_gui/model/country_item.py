from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.enums import ServerStatusEnum, ServerTierEnum, FeatureEnum
from protonvpn_nm_lib.country_codes import country_codes
from .server_item import ServerItem


class CountryItem:
    """CountryItem class.

    Represents a country item in the list of servers. This object stores
    information about a country and also a list of servers that it provides.

    Properties:
        country_name : str
            country name that is set by the view
        entry_country_code: str
            ISO country code
        status: ServerStatusEnum
            country server status
        tiers: list
            the tiers that this country has
        features: list
            features that this country provides
        servers: list
            contains a list of ServerItem

    All the properties can be reacheched from the outside, but only two can be
    set outside of it's own class, entry_country_code and country_name.

    entry_country_code: this is set in the class that builds this object,
    thus avoiding to pass any the country code as an argument.

    country_name: since country names are dependt on
    heir translation (view level) so it does not make sense to hard-code
    it here. Also, this property, after being set, shall be used to
    sort countries in alphabetical order.
    """
    def __init__(self):
        self.__entry_country_code: str = None
        self.__status: ServerStatusEnum = None
        self.__tiers: list = list()
        self.__features: list = set()
        self.__servers: list = list()
        self.__can_connect: bool = False
        self.__minimum_required_tier = None
        self.__host_country: str = None
        self.__is_virtual_country: bool = None
        self.__country_name: str = None
        self.__num_free_countries: int = None
        self.__num_basic_countries: int = None
        self.__num_plus_countries: int = None
        self.__num_internal_countries: int = None

    def __len__(self):
        return len(self.__servers)

    @property
    def country_name(self):
        return self.__country_name

    @country_name.setter
    def country_name(self, new_country_name):
        self.__country_name = new_country_name

    @property
    def entry_country_code(self):
        return self.__entry_country_code

    @entry_country_code.setter
    def entry_country_code(self, new_entry_country_code):
        self.__entry_country_code = new_entry_country_code

    @property
    def status(self):
        return self.__status

    @property
    def tiers(self):
        return self.__tiers

    @property
    def features(self):
        return self.__features

    @property
    def servers(self):
        return self.__servers

    @servers.setter
    def servers(self, newvalue):
        self.__servers = newvalue

    @property
    def can_connect(self):
        return self.__can_connect

    @property
    def country_tier(self):
        return self.__minimum_required_tier

    @country_tier.setter
    def minimum_country_tier(self, _value):
        self.__minimum_required_tier = _value

    @property
    def is_virtual(self):
        return self.__is_virtual_country

    @property
    def ammount_of_free_servers(self):
        if self.__num_free_countries is None:
            self.__num_free_countries = 0
            for server in self.servers:
                if server.tier == ServerTierEnum.FREE:
                    self.__num_free_countries += 1

        return self.__num_free_countries

    @property
    def ammount_of_basic_servers(self):
        if self.__num_basic_countries is None:
            self.__num_basic_countries = 0
            for server in self.servers:
                if server.tier == ServerTierEnum.BASIC:
                    self.__num_basic_countries += 1

        return self.__num_basic_countries

    @property
    def ammount_of_plus_servers(self):
        if self.__num_plus_countries is None:
            self.__num_plus_countries = 0
            for server in self.servers:
                if server.tier == ServerTierEnum.PLUS_VISIONARY:
                    self.__num_plus_countries += 1

        return self.__num_plus_countries

    @property
    def ammount_of_internal_servers(self):
        if self.__num_internal_countries is None:
            self.__num_internal_countries = 0
            for server in self.servers:
                if server.tier.value >= ServerTierEnum.PM.value:
                    self.__num_internal_countries += 1

        return self.__num_internal_countries

    def create(
        self, user_tier, servername_list
    ):
        status_collector = set()
        tier_collector = set()
        feature_collector = set()
        country_host_collection = list()
        self.__host_country = set()

        for servername in servername_list:
            logical_server = protonvpn.get_session().servers.filter(
                lambda server: server.name.lower() == servername.lower()
            )[0]
            server_item = ServerItem(logical_server)
            self.__servers.append(server_item)
            self.__add_feature_to_feature_collector(
                feature_collector, server_item.features
            )
            self.__add_status_to_status_collector(
                status_collector, server_item.status
            )
            self.__add_tier_to_tier_collector(tier_collector, server_item.tier)
            if FeatureEnum.SECURE_CORE in logical_server.features:
                continue
            country_host_collection.append(logical_server.host_country)

        self.__set_features(feature_collector)
        self.__set_status(status_collector)
        self.__set_tiers(tier_collector)
        self.__set_minimum_required_tier(tier_collector)
        self.__country_name = country_codes.get(
            self.__entry_country_code,
            self.__entry_country_code
        )
        self.__can_connect = True\
            if (
                (
                    user_tier == ServerTierEnum.FREE
                    and ServerTierEnum.FREE in self.__tiers
                ) or (
                    user_tier.value > ServerTierEnum.FREE.value
                )

            ) else False
        self.__is_virtual_country = all(host_country for host_country in country_host_collection)

    def __add_feature_to_feature_collector(
        self, feature_collector, server_features
    ):
        for feature in server_features:
            feature_collector.add(feature)

    def __add_status_to_status_collector(self, status_collector, server_status):
        status_collector.add(server_status)

    def __add_tier_to_tier_collector(self, tier_collector, server_tier):
        tier_collector.add(server_tier)

    def __set_features(self, features_collector):
        self.__features = list(features_collector)

    def __set_status(self, status_collector):
        self.__status = self.__get_country_status(
            list(status_collector)
        )

    def __set_tiers(self, tier_collector):
        self.__tiers = list(tier_collector)

    def __set_minimum_required_tier(self, tier_collector):
        for tier in tier_collector:
            if not self.__minimum_required_tier:
                self.__minimum_required_tier = tier
                continue
            elif self.__minimum_required_tier.value > tier.value:
                self.__minimum_required_tier = tier

    def __get_country_status(self, status_collector):
        if len(status_collector) == 2:
            return ServerStatusEnum.ACTIVE
        elif (
            status_collector
            and status_collector.pop() == ServerStatusEnum.ACTIVE
        ):
            return ServerStatusEnum.ACTIVE
        else:
            return ServerStatusEnum.UNDER_MAINTENANCE
