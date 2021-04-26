import os
from abc import abstractmethod

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, Gtk

from ..constants import CSS_DIR_PATH, UI_DIR_PATH
from ..factory.abstract_widget_factory import WidgetFactory


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "server_features.ui"))
class ServerFeaturesView(Gtk.ApplicationWindow):
    """ServerFeatures view class. GTK Composite object."""
    __gtype_name__ = "ServerFeaturesView"

    server_features_container_grid = Gtk.Template.Child()

    def __init__(self, application):
        super().__init__(application=application)
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(
            os.path.join(CSS_DIR_PATH, "server_features.css")
        )
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.set_position(Gtk.PositionType.BOTTOM)

    def display(self):
        """Display object."""
        self.present()

    @property
    def title(self):
        return self.get_title()

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
        self.__widget = ServerFeaturesView(application)
        self.__widget.title = "Features"
        self.__create_widgets()
        self.__attach_widgets()
        self.__widget.display()

    def __create_widgets(self):
        self.__create_smart_routing_widget()
        self.__create_streaming_widget()
        self.__create_p2p_widget()
        self.__create_tor_widget()

    def __attach_widgets(self):
        self.__widget.server_features_container_grid.attach(
            self.smart_routing.widget, 0, 0, 1, 1
        )
        self.__widget.server_features_container_grid.attach(
            self.streaming.widget, 0, 1, 1, 1
        )
        self.__widget.server_features_container_grid.attach(
            self.peer2peer.widget, 0, 2, 1, 1
        )
        self.__widget.server_features_container_grid.attach(
            self.tor.widget, 0, 3, 1, 1
        )

    def __create_smart_routing_widget(self):
        self.smart_routing = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_smart_routing")
        title = WidgetFactory.label("premium_features_popover_title")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        title.content = "Smart Routing"
        description.content = "This technology allows ProtonVPN to provide higher" \
            "speed and security in difficult-to-server countries."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/smart-routing//"

        self.smart_routing.attach(feature_logo.widget)
        self.smart_routing.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.smart_routing.attach_bottom_next_to(
            description.widget, title.widget
        )
        self.smart_routing.attach_bottom_next_to(
            view_more_link.widget, description.widget
        )

    def __create_streaming_widget(self):
        self.streaming = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_streaming")
        title = WidgetFactory.label("premium_features_popover_title")
        description = WidgetFactory.label("premium_features_popover_description")
        view_more_link = WidgetFactory.button("learn_more")
        view_more_link.add_class("padding-x-none")
        view_more_link.add_class("margin-left-10px")

        title.content = "Streaming"
        description.content = "PLUS seerver support streaming (Netflix, Disney+, etc) " \
            "from anywhere in the world."
        view_more_link.label = "Learn more"
        view_more_link.url = "https://protonvpn.com/support/streaming-guide/"

        self.streaming.attach(feature_logo.widget)
        self.streaming.attach_right_next_to(
            title.widget, feature_logo.widget
        )
        self.streaming.attach_bottom_next_to(
            description.widget, title.widget
        )
        self.streaming.attach_bottom_next_to(
            view_more_link.widget, description.widget
        )

    def __create_p2p_widget(self):
        self.peer2peer = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_p2p")
        title = WidgetFactory.label("premium_features_popover_title")
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
        self.peer2peer.attach_bottom_next_to(
            description.widget, title.widget
        )
        self.peer2peer.attach_bottom_next_to(
            view_more_link.widget, description.widget
        )

    def __create_tor_widget(self):
        self.tor = WidgetFactory.grid("default")
        feature_logo = WidgetFactory.image("premium_popover_tor")
        title = WidgetFactory.label("premium_features_popover_title")
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
        self.tor.attach_bottom_next_to(
            description.widget, title.widget
        )
        self.tor.attach_bottom_next_to(
            view_more_link.widget, description.widget
        )
