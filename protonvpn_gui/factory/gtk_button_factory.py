from abc import ABCMeta
from ..utils import SubclassesMixin

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk


class GtkButton(SubclassesMixin, metaclass=ABCMeta):

    def __init__(self):
        self.__button = Gtk.Button()
        self.__button_context = self.__button.get_style_context()

    @classmethod
    def factory(cls, button):
        buttons_dict = cls._get_subclasses_dict("button")
        return buttons_dict[button]()

    @property
    def widget(self):
        """Get buttons object."""
        return self.__button

    @property
    def context(self):
        return self.__button_context

    @property
    def label(self):
        """Get buttons labels."""
        return self.__button.props.label

    @label.setter
    def label(self, newvalue):
        """Set buttons labels.

        Args:
            newvalue (string)
        """
        self.__button.props.label = newvalue

    @property
    def image(self):
        """Get buttons image.

        This property replaces the label property.
        """
        return self.__button.props.image

    @image.setter
    def image(self, newvalue):
        """Set buttons labels.

        This property replaces the label property.
        """
        self.__button.props.image = newvalue

    @property
    def show(self):
        """Get button visibility."""
        return self.__button.props.visible

    @show.setter
    def show(self, newvalue):
        """Set button visibiltiy."""
        self.__button.props.visible = newvalue

    @property
    def expand_h(self):
        """Get horizontal expand."""
        return self.__button.get_hexpand()

    @expand_h.setter
    def expand_h(self, newvalue):
        """Set horizontal expand."""
        self.__button.set_hexpand(newvalue)

    @property
    def expand_v(self):
        """Get vertical expand."""
        return self.__button.get_vexpand()

    @expand_v.setter
    def expand_v(self, newvalue):
        """Set vertical expand."""
        self.__button.set_vexpand(newvalue)

    @property
    def align_h(self):
        """Get horizontal align."""
        return self.__button.get_halign()

    @align_h.setter
    def align_h(self, newvalue):
        """Set horizontal align."""
        return self.__button.set_halign(newvalue)

    @property
    def align_v(self):
        """Get vertical align."""
        return self.__button.get_valign()

    @align_v.setter
    def align_v(self, newvalue):
        """Set vertical align."""
        return self.__button.set_valign(newvalue)

    def add_class(self, css_class):
        """Add CSS class."""
        self.__button_context.add_class(css_class)

    def remove_class(self, css_class):
        """Remove CSS class."""
        if self.has_class(css_class):
            self.__button_context.remvove_class(css_class)

    def has_class(self, css_class):
        """Check if has CSS class."""
        return True if self.__button_context.has_class(css_class) else False

    def connect(self, *args, **kwargs):
        self.__button.connect(*args, **kwargs)


class DefaultGtkButton(GtkButton):
    button = "gtk_default"

    def __init__(self):
        super().__init__()
        self.name = "Default Gtk button"


class MainConnectButton(GtkButton):
    button = "main_connect"

    def __init__(self):
        super().__init__()
        self.name = "Main Connect button"


class MainDisconnectButton(GtkButton):
    button = "main_disconnect"

    def __init__(self):
        super().__init__()
        self.name = "Main Disconnect button"


class ConnectToServerButton(GtkButton):
    button = "connect"

    def __init__(self):
        super().__init__()
        self.name = "Connect button"
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.add_class("transparent")
        self.label = "CONNECT"


class DisconnectFromServerButton(GtkButton):
    button = "disconnect"

    def __init__(self):
        super().__init__()
        self.name = "Disconnect from server button"
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.add_class("transparent")
        self.label = "DISCONNECT"


class TransparentButton(GtkButton):
    button = "transparent"

    def __init__(self):
        super().__init__()
        self.name = "Transparent button"


class ChevronButton(GtkButton):
    button = "chevron"

    def __init__(self):
        super().__init__()
        self.name = "chevron button"
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.align_h = Gtk.Align.END
        self.show = True
        self.add_class("chevron-unfold")
