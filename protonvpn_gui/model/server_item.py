from protonvpn_nm_lib.enums import (FeatureEnum, ServerStatusEnum,
                                    ServerTierEnum)


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
    """
    name: str = None
    load: int = None
    city: str = None
    features: list = None
    tier: int = None
    is_plus: bool = None
    status: int = None
    exit_country_code: str = None

    @staticmethod
    def create(logical_server):
        server_item = ServerItem()
        server_item.name = logical_server.name
        server_item.load = str(int(logical_server.load))
        server_item.city = logical_server.city
        server_item.features = [FeatureEnum(logical_server.features)]
        server_item.tier = ServerTierEnum(logical_server.tier)
        server_item.is_plus = server_item.check_server_item_is_plus(
            server_item
        )
        server_item.status = ServerStatusEnum(logical_server.status)
        server_item.exit_country_code = logical_server.exit_country

        return server_item

    def check_server_item_is_plus(self, server_item):
        if server_item.tier.value < ServerTierEnum.PLUS_VISIONARY.value:
            return False

        return True
