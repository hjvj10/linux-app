from protonvpn_nm_lib.enums import ServerTierEnum, FeatureEnum
from abc import abstractmethod, ABCMeta
from ..utils import SubclassesMixin


class ServerType(SubclassesMixin, metaclass=ABCMeta):
    @classmethod
    def factory(cls, type="default"):
        subclasses_dict = cls._get_subclasses_dict("server_type")
        return subclasses_dict[type]()

    @property
    @abstractmethod
    def user_tier():
        raise NotImplementedError()

    @user_tier.setter
    @abstractmethod
    def user_tier():
        raise NotImplementedError()

    @property
    @abstractmethod
    def servers():
        raise NotImplementedError()

    @servers.setter
    def servers():
        raise NotImplementedError()

    @property
    @abstractmethod
    def total_countries_count():
        raise NotImplementedError()

    @property
    @abstractmethod
    def free_countries_count():
        raise NotImplementedError()

    @property
    @abstractmethod
    def basic_countries_count():
        raise NotImplementedError()

    @property
    @abstractmethod
    def plus_countries_count():
        raise NotImplementedError()

    @property
    @abstractmethod
    def internal_countries_count():
        raise NotImplementedError()

    @abstractmethod
    def generate():
        raise NotImplementedError()


class SecureCoreServers(ServerType):
    server_type = "secure_core_default"

    def __init__(self):
        self.__servers = []
        self.__user_tier = None

    @property
    def user_tier(self):
        return self.__user_tier

    @user_tier.setter
    def user_tier(self, newvalue):
        self.__user_tier = newvalue

    @property
    def servers(self):
        return self.__servers

    @servers.setter
    def servers(self, newvalue):
        self.__servers = newvalue

    @property
    def total_countries_count(self):
        pass

    @property
    def free_countries_count(self):
        pass

    @property
    def basic_countries_count(self):
        pass

    @property
    def plus_countries_count(self):
        pass

    @property
    def internal_countries_count(self):
        pass

    def generate(self, unfiltered_server_list):
        self.__servers = []
        for country_item in unfiltered_server_list:
            country_item.servers = list(filter(
                lambda server: any(
                    feature == FeatureEnum.SECURE_CORE
                    for feature
                    in server.features
                ), country_item.servers
            ))

            self.__servers.append(country_item)
        self.__servers.sort(key=lambda c: c.country_name)

        return self.__servers


class NonSecureCoreServers(ServerType):
    server_type = "non_secure_core_default"

    def __init__(self):
        self.__servers = []
        self.__user_tier = None
        self.sort_methods_by_tier = {
            ServerTierEnum.FREE: self._sort_for_free_user,
            ServerTierEnum.BASIC: self._sort_for_basic_user,
            ServerTierEnum.PLUS_VISIONARY: self._sort_for_plus_user,
            ServerTierEnum.PM: self._sort_for_internal_user,
        }

    @property
    def user_tier(self):
        return self.__user_tier

    @user_tier.setter
    def user_tier(self, newvalue):
        self.__user_tier = newvalue

    @property
    def servers(self):
        return self.__servers

    @servers.setter
    def servers(self, newvalue):
        self.__servers = newvalue

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
            country_item.servers = list(filter(
                lambda server: all(
                    feature != FeatureEnum.SECURE_CORE
                    for feature
                    in server.features
                ), country_item.servers
            ))

            country_item.servers = self._default_sort(
                country_item
            )
            self.__servers.append(country_item)

        try:
            self.sort_methods_by_tier[self.__user_tier]()
        except KeyError:
            self.__sort_for_free_users()

        return self.__servers

    def _default_sort(self, country_item):
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

    def _sort_for_free_user(self):
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

    def _sort_for_basic_user(self):
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

    def _sort_for_plus_user(self):
        self.__servers.sort(
            key=lambda country: country.country_name
        )

    def _sort_for_internal_user(self):
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
