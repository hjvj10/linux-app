from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.enums import ServerStatusEnum, ServerTierEnum


class ServerItem:
    """ServerItem class.

    Represents a server item in the list of servers. This object stores
    information about a server.

    Properties:
        name : str
            servername
        load: str
            server load
        city: str
            city where the server is located
        features: list
            list of features
        tier: ServerTierEnum
            server tier
        is_plus: bool
            if server is a plus server (shortcut property for tier)
        status: ServerStatusEnum
            server status
        exit_country_code: str
            ISO country code of this servers country
        has_to_upgrade: bool
            if a user has to upgrade to access server
    """
    def __init__(self, logical_server):
        self.__name: str = None
        self.__load: int = None
        self.__score: int = None
        self.__city: str = None
        self.__features: list = []
        self.__tier: ServerTierEnum = None
        self.__is_plus: bool = None
        self.__status: int = None
        self.__exit_country_code: str = None
        self.__entry_country_code: str = None
        self.__has_to_upgrade: bool = None
        self.__host_country: str = None
        self.create(logical_server)

    @property
    def name(self):
        return self.__name

    @property
    def load(self):
        return self.__load

    @property
    def score(self):
        return self.__score

    @property
    def city(self):
        return self.__city

    @property
    def features(self):
        return self.__features

    @property
    def tier(self):
        return self.__tier

    @property
    def is_plus(self):
        return self.__is_plus

    @property
    def status(self):
        return self.__status

    @property
    def exit_country_code(self):
        return self.__exit_country_code

    @property
    def entry_country_code(self):
        return self.__entry_country_code

    @property
    def has_to_upgrade(self):
        return self.__has_to_upgrade

    @property
    def host_country(self):
        return self.__host_country

    def create(self, logical_server):
        self.__name = logical_server.name
        self.__load = str(int(logical_server.load))
        self.__score = int(logical_server.score)
        self.__city = logical_server.city
        self.__features = logical_server.features
        self.__tier = ServerTierEnum(logical_server.tier)
        self.__is_plus = self.__check_server_is_plus()
        self.__status = ServerStatusEnum(logical_server.enabled)
        self.__exit_country_code = logical_server.exit_country
        self.__entry_country_code = logical_server.entry_country
        self.__host_country = logical_server.host_country
        self.__has_to_upgrade = (
            True if self.__tier.value > ServerTierEnum(
                protonvpn.get_session().vpn_tier
            ).value else False
        )

    def __check_server_is_plus(self):
        if self.__tier.value < ServerTierEnum.PLUS_VISIONARY.value:
            return False

        return True
