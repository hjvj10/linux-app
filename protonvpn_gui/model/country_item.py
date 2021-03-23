from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.enums import (FeatureEnum, ServerStatusEnum,
                                    ServerTierEnum)

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
    def __init__(self, server_item=ServerItem):
        self._server_item: ServerItem = server_item

        self._entry_country_code: str = None
        self._status: ServerStatusEnum = None
        self._tiers: list = list()
        self._features: list = set()
        self._servers: list = list()
        self._available_to_free_users: bool = False

        # This is set on the view.
        self._country_name = None

    @property
    def country_name(self):
        return self._country_name

    @country_name.setter
    def country_name(self, new_country_name):
        self._country_name = new_country_name

    @property
    def entry_country_code(self):
        return self._entry_country_code

    @entry_country_code.setter
    def entry_country_code(self, new_entry_country_code):
        self._entry_country_code = new_entry_country_code

    @property
    def status(self):
        return self._status

    @property
    def tiers(self):
        return self._tiers

    @property
    def features(self):
        return self._features

    @property
    def servers(self):
        return self._servers

    @property
    def available_to_free_users(self):
        return self._available_to_free_users

    def create_secure_core_country(
        self, servername_list, server_list
    ):
        status_collector = set()
        tier_collector = set()
        feature_collector = set()

        for servername in servername_list:
            logical_server = protonvpn.get_session().servers.filter(
                lambda server: server.name.lower() == servername.lower()
            )[0]

            server_item = self._server_item.create(logical_server)
            if (
                not any(
                    feature == FeatureEnum.SECURE_CORE
                    for feature
                    in server_item.features
                )
            ):
                continue

            self._servers.append(server_item)
            self.add_feature_to_feature_collector(
                feature_collector, server_item
            )
            self.add_status_to_status_collector(
                status_collector, server_item
            )
            self.add_tier_to_tier_collector(tier_collector, server_item)

        self.set_features(feature_collector)
        self.set_status(status_collector)
        self.set_tiers(tier_collector)
        self._available_to_free_users = True\
            if ServerTierEnum in self._tiers else False

    def create_non_secure_core_country(
        self, user_tier, servername_list, server_list
    ):
        status_collector = set()
        tier_collector = set()
        feature_collector = set()

        for servername in servername_list:
            logical_server = protonvpn.get_session().servers.filter(
                lambda server: server.name.lower() == servername.lower()
            )[0]
            server_item = self._server_item.create(logical_server)
            if (
                any(
                    feature == FeatureEnum.SECURE_CORE
                    for feature
                    in server_item.features
                )
            ):
                continue

            self._servers.append(server_item)
            self.add_feature_to_feature_collector(
                feature_collector, server_item.features
            )
            self.add_status_to_status_collector(
                status_collector, server_item.status
            )
            self.add_tier_to_tier_collector(tier_collector, server_item.tier)

        self.set_features(feature_collector)
        self.set_status(status_collector)
        self.set_tiers(tier_collector)
        self._available_to_free_users = True\
            if (
                (
                    user_tier == ServerTierEnum.FREE
                    and ServerTierEnum.FREE in self._tiers
                ) or (
                    user_tier.value > ServerTierEnum.FREE.value
                )

            ) else False

    def add_feature_to_feature_collector(
        self, feature_collector, server_features
    ):
        feature_collector.add(*server_features)

    def add_status_to_status_collector(self, status_collector, server_status):
        status_collector.add(server_status)

    def add_tier_to_tier_collector(self, tier_collector, server_tier):
        tier_collector.add(server_tier)

    def set_features(self, features_collector):
        self._features = list(features_collector)

    def set_status(self, status_collector):
        self._status = self.get_country_status(
            list(status_collector)
        )

    def set_tiers(self, tier_collector):
        self._tiers = list(tier_collector)

    def get_country_status(self, status_collector):
        if len(status_collector) == 2:
            return ServerStatusEnum.ACTIVE
        elif (
            status_collector
            and status_collector.pop() == ServerStatusEnum.ACTIVE
        ):
            return ServerStatusEnum.ACTIVE
        else:
            return ServerStatusEnum.UNDER_MAINTENANCE
