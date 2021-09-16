from protonvpn_nm_lib.enums import ServerTierEnum, FeatureEnum
import copy


class SecureCoreServers:

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

            self.__servers.append(copy_country_item)
        self.__servers.sort(key=lambda c: c.country_name)
