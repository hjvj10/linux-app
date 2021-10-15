from .utils import Singleton


class Module(metaclass=Singleton):

    def __init__(self):
        # Model
        self.__server_item_model = None
        self.__country_item_model = None

        self.__non_secure_core_servers_model = None
        self.__secure_core_servers_model = None

        self.__server_list_model = None

        # ViewModel
        self.__login_view_model = None
        self.__dashboard_view_model = None
        self.__quick_settings_view_model = None
        self.__server_list_view_model = None

        # Utils
        self.__utils = None

    @property
    def server_item_model(self):
        """Return server item model"""
        if self.__server_item_model is None:
            from .model import ServerItemFactory
            self.__server_item_model = ServerItemFactory.factory()
        return self.__server_item_model

    @server_item_model.setter
    def server_item_model(self, newvalue):
        self.__server_item_model = newvalue

    @property
    def country_item_model(self):
        """Return country item model"""
        if self.__country_item_model is None:
            from .model import CountryItemFactory
            self.__country_item_model = CountryItemFactory.factory()
        return self.__country_item_model

    @country_item_model.setter
    def country_item_model(self, newvalue):
        self.__country_item_model = newvalue

    @property
    def non_secure_core_servers_model(self):
        """Return non-secure-core servers model"""
        if self.__non_secure_core_servers_model is None:
            from .model import ServerType
            self.__non_secure_core_servers_model = ServerType.factory("non_secure_core_default")
        return self.__non_secure_core_servers_model

    @non_secure_core_servers_model.setter
    def non_secure_core_servers_model(self, newvalue):
        self.__non_secure_core_servers_model = newvalue

    @property
    def secure_core_servers_model(self):
        """Return Secure-Core servers model"""
        if self.__secure_core_servers_model is None:
            from .model import ServerType
            self.__secure_core_servers_model = ServerType.factory("secure_core_default")
        return self.__secure_core_servers_model

    @secure_core_servers_model.setter
    def secure_core_servers_model(self, newvalue):
        self.__secure_core_servers_model = newvalue

    @property
    def server_list_model(self):
        """Return server list model"""
        if self.__server_list_model is None:
            from .model import ServerList
            self.__server_list_model = ServerList()
        return self.__server_list_model

    @server_list_model.setter
    def server_list_model(self, newvalue):
        self.__server_list_model = newvalue

    @property
    def login_view_model(self):
        """Return login view model"""
        if self.__login_view_model is None:
            from .view_model import LoginViewModel
            self.__login_view_model = LoginViewModel()
        return self.__login_view_model

    @login_view_model.setter
    def login_view_model(self, newvalue):
        self.__login_view_model = newvalue

    @property
    def dashboard_view_model(self):
        """Return dashboard view model"""
        if self.__dashboard_view_model is None:
            from .view_model import DashboardViewModel
            self.__dashboard_view_model = DashboardViewModel()
        return self.__dashboard_view_model

    @dashboard_view_model.setter
    def dashboard_view_model(self, newvalue):
        self.__dashboard_view_model = newvalue

    @property
    def quick_settings_view_model(self):
        """Return quick-settings view model"""
        if self.__quick_settings_view_model is None:
            from .view_model import QuickSettingsViewModel
            self.__quick_settings_view_model = QuickSettingsViewModel()
        return self.__quick_settings_view_model

    @quick_settings_view_model.setter
    def quick_settings_view_model(self, newvalue):
        self.__quick_settings_view_model = newvalue

    @property
    def server_list_view_model(self):
        """Return server list view model"""
        if self.__server_list_view_model is None:
            from .view_model import ServerListViewModel
            self.__server_list_view_model = ServerListViewModel()
        return self.__server_list_view_model

    @server_list_view_model.setter
    def server_list_view_model(self, newvalue):
        self.__server_list_view_model = newvalue

    @property
    def utility(self):
        """Return utilities"""
        if self.__utils is None:
            from .model import Utilities
            self.__utils = Utilities()
        return self.__utils

    @utility.setter
    def utility(self, newvalue):
        self.__utils = newvalue
