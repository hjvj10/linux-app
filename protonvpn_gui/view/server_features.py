import os
from abc import abstractmethod
from protonvpn_nm_lib.api import protonvpn
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, Gtk

from ..constants import CSS_DIR_PATH, UI_DIR_PATH
from ..patterns.factory.abstract_widget_factory import WidgetFactory


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "server_features.ui"))
class ServerFeaturesView(Gtk.ApplicationWindow):
    """ServerFeatures view class. GTK Composite object."""
    __gtype_name__ = "ServerFeaturesView"

    server_features_container_grid = Gtk.Template.Child()
    scrolled_window = Gtk.Template.Child()

    def __init__(self, application):
        super().__init__(application=application)
        _provider = Gtk.CssProvider()
        _provider.load_from_path(
            os.path.join(CSS_DIR_PATH, "server_features.css")
        )
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            _provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.set_position(Gtk.PositionType.BOTTOM)

    def display(self):
        """Display object."""
        self.present()

    @property
    def title(self):
        return self.get_title()

    def attach(self, widget, column=0, row=0, width=1, height=1):
        self.server_features_container_grid.attach(widget, column, row, width, height)

    @title.setter
    def title(self, newvalue):
        return self.set_title(newvalue)

    @abstractmethod
    def __create_widgets():
        """Private method that creates widgets"""
        pass

    @abstractmethod
    def __attach_widgets():
        """Private method that attaches widgets to main container grid"""
        pass


class PremiumCountries():
    def __init__(self, application):
        self.__view = ServerFeaturesView(application)
        self.__view.title = "Features"
        self.__view_list = []
        self.__create_widgets()
        self.__attach_widgets()
        self.__view.display()

    def __create_widgets(self):
        self.__create_p2p_widget()
        self.__create_streaming_widget()
        self.__create_smart_routing_widget()
        self.__create_tor_widget()

    def __attach_widgets(self):
        counter = 0
        for wiget in self.__view_list:
            self.__view.attach(wiget.widget, row=counter)
            counter += 1

    def __create_smart_routing_widget(self):
        self.smart_routing = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_smart_routing")
        title = WidgetFactory.label("premium_features_popover_title")
        tier_chip = WidgetFactory.label("premium_features_popover_chip", "PLUS")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        title.content = "Smart Routing"
        description.content = "This technology allows ProtonVPN to provide higher" \
            "speed and security in difficult-to-serve countries."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/smart-routing//"

        self.smart_routing.attach(feature_logo.widget)
        self.smart_routing.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.smart_routing.attach_right_next_to(
            tier_chip.widget, title.widget
        )
        self.smart_routing.attach_bottom_next_to(
            description.widget, title.widget, width=2
        )
        self.smart_routing.attach_bottom_next_to(
            view_more_link.widget, description.widget, width=2
        )
        self.__view_list.append(self.smart_routing)

    def __create_streaming_widget(self):
        self.streaming = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_streaming")
        title = WidgetFactory.label("premium_features_popover_title")
        tier_chip = WidgetFactory.label("premium_features_popover_chip", "PLUS")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        title.content = "Streaming"
        description.content = "PLUS server support streaming (Netflix, Disney+, etc) " \
            "from anywhere in the world."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/streaming-guide/"

        self.streaming.attach(feature_logo.widget,)
        self.streaming.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.streaming.attach_right_next_to(
            tier_chip.widget, title.widget
        )
        self.streaming.attach_bottom_next_to(
            description.widget, title.widget, width=2
        )
        self.streaming.attach_bottom_next_to(
            view_more_link.widget, description.widget, width=2
        )
        self.__view_list.append(self.streaming)

    def __create_p2p_widget(self):
        self.peer2peer = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_p2p")
        title = WidgetFactory.label("premium_features_popover_title")
        tier_chip = WidgetFactory.label("premium_features_popover_chip", "BASIC & PLUS")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")

        title.content = "P2P/BitTorrent"
        description.content = "These servers give the best performance for BitTorrent "\
            "and file sharing."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/bittorrent-vpn/"
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        self.peer2peer.attach(feature_logo.widget)
        self.peer2peer.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.peer2peer.attach_right_next_to(
            tier_chip.widget, title.widget
        )
        self.peer2peer.attach_bottom_next_to(
            description.widget, title.widget, width=2
        )
        self.peer2peer.attach_bottom_next_to(
            view_more_link.widget, description.widget, width=2
        )
        self.__view_list.append(self.peer2peer)

    def __create_tor_widget(self):
        self.tor = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_tor")
        title = WidgetFactory.label("premium_features_popover_title")
        tier_chip = WidgetFactory.label("premium_features_popover_chip", "PLUS")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")

        title.content = "Tor"
        description.content = "Route your Internet traffic through the Tor network. "\
            "Slower but more private."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/tor-vpn/"
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        self.tor.attach(feature_logo.widget)
        self.tor.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.tor.attach_right_next_to(
            tier_chip.widget, title.widget
        )
        self.tor.attach_bottom_next_to(
            description.widget, title.widget, width=2
        )
        self.tor.attach_bottom_next_to(
            view_more_link.widget, description.widget, width=2
        )
        self.__view_list.append(self.tor)


class PlusFeatures:
    """Plus Features class.

    This class should be used when there is need to display multiple features
    for a given country.

    It stores an internal list with widgets that will be added and displayed to the user
    (in the order that they are appended to the list inside __generate_widgets(). To add more
    features to a given country ensure that your class has a public generate_widget() method
    in which it return an object generated from the widget factory.
    """
    def __init__(self, application, country):
        self.__view = ServerFeaturesView(application)
        self.__view.title = "Features"
        self.__view_list = []
        self.__generate_widgets(application, country)
        self.__attach_widgets()
        self.__view.display()

    def __generate_widgets(self, application, country):
        """Genrates widget and append to internal list.

        Args:
            application (Gtk.Application): application object
            country (CountryItem): country object
        """
        self.__view_list.append(
            CountryStreamingWidget(application, country, True).generate_widget()
        )

    def __attach_widgets(self):
        """Attach widgets to view."""
        counter = 0
        for _widget in self.__view_list:
            self.__view.attach(_widget.widget, row=counter)
            counter += 1


class CountryStreamingWidget:
    """Country Streaming widget.

    This widget displays streamig information in relation to the
    provided country. If this widget belongs in a list of features (is part
    of PlusFeatures) then parent_widget variable contains the widget
    created in the parent class, thus it should only instatiate the class and set the internal
    country and widget variables so that the parent can call generate_widget() whenever needed.

    Otherwise, it behaves as if only streaming information about the specified country
    is to be displayed.
    """
    def __init__(self, application, country, parent_widget=False):
        self.country = country

        if parent_widget:
            self.__view = parent_widget
            return

        self.__view = ServerFeaturesView(application)
        self.__view.title = "Streaming"
        self.__view.attach(self.generate_widget(country).widget)
        self.__view.display()

    def generate_widget(self):
        _widget = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_streaming")
        title = WidgetFactory.label("premium_features_popover_title")
        description = WidgetFactory.label("streaming_description")

        title.content = "Streaming - {}".format(self.country.country_name)
        description.content = "Connect to a Plus server in this country to start streaming." \
            "\n\nNote: Use a new browser tab and/or clear the cache to ensure new content appears."

        supported_services = self.__add_supported_services()
        _widget.attach(feature_logo.widget)
        _widget.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        _widget.attach_bottom_next_to(
            description.widget, title.widget
        )
        _widget.attach_bottom_next_to(
            supported_services.widget, description.widget
        )
        description = WidgetFactory.label("streaming_description", "and more")
        _widget.attach_bottom_next_to(
            description.widget, supported_services.widget
        )
        return _widget

    def __add_supported_services(self):
        streaming_services = protonvpn.get_session().streaming
        streaming_icons = protonvpn.get_session().streaming_icons
        client_config = protonvpn.get_session().clientconfig

        try:
            services = streaming_services[self.country.entry_country_code]
        except KeyError:
            return

        services.sort(key=lambda service: service["Name"])
        services_grid = WidgetFactory.grid("streaming_icons_container")
        x_pos = 0
        y_pos = 0
        max_items_per_row = 3
        for service in services:
            if client_config.features.streaming_logos and streaming_icons[service.get("Icon")]:
                service_widget = WidgetFactory.image(
                    "streaming_service_icon", streaming_icons[service.get("Icon")]
                )
            else:
                service_widget = WidgetFactory.label(
                    "streaming_title", service["Name"]
                )

            services_grid.attach(service_widget.widget, x_pos, y_pos)

            if x_pos == (max_items_per_row - 1):
                y_pos += 1
                x_pos = 0
            else:
                x_pos += 1

        return services_grid
