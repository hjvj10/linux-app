from abc import ABCMeta

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from ..abstract_widget_factory import WidgetFactory


class ButtonFactory(WidgetFactory, metaclass=ABCMeta):
    """Concrete Button Factory class."""

    concrete_factory = "button"

    def __init__(self):
        self.__widget = Gtk.Button()
        self.__widget_context = self.__widget.get_style_context()

    @classmethod
    def factory(cls, widget_name):
        subclasses_dict = cls._get_subclasses_dict("button")
        return subclasses_dict[widget_name]()

    @property
    def widget(self):
        """Get widget object."""
        return self.__widget

    @property
    def context(self):
        return self.__widget_context

    @property
    def label(self):
        """Get widget label."""
        return self.__widget.props.label

    @label.setter
    def label(self, newvalue):
        """Set widget label.

        Args:
            newvalue (string)
        """
        self.__widget.props.label = newvalue

    @property
    def image(self):
        """Get widget image.

        This property replaces the label property.
        """
        return self.__widget.props.image

    @image.setter
    def image(self, newvalue):
        """Set widget image.

        This property replaces the label property.
        """
        self.__widget.props.image = newvalue

    @property
    def show(self):
        """Get widget visibility."""
        return self.__widget.props.visible

    @show.setter
    def show(self, newvalue):
        """Set widget visibiltiy."""
        self.__widget.props.visible = newvalue

    @property
    def expand_h(self):
        """Get horizontal expand."""
        return self.__widget.get_hexpand()

    @expand_h.setter
    def expand_h(self, newvalue):
        """Set horizontal expand."""
        self.__widget.set_hexpand(newvalue)

    @property
    def expand_v(self):
        """Get vertical expand."""
        return self.__widget.get_vexpand()

    @expand_v.setter
    def expand_v(self, newvalue):
        """Set vertical expand."""
        self.__widget.set_vexpand(newvalue)

    @property
    def align_h(self):
        """Get horizontal align."""
        return self.__widget.get_halign()

    @align_h.setter
    def align_h(self, newvalue):
        """Set horizontal align."""
        return self.__widget.set_halign(newvalue)

    @property
    def align_v(self):
        """Get vertical align."""
        return self.__widget.get_valign()

    @align_v.setter
    def align_v(self, newvalue):
        """Set vertical align."""
        return self.__widget.set_valign(newvalue)

    def add_class(self, css_class):
        """Add CSS class."""
        self.__widget_context.add_class(css_class)

    def remove_class(self, css_class):
        """Remove CSS class."""
        if self.has_class(css_class):
            self.__widget_context.remove_class(css_class)

    def has_class(self, css_class):
        """Check if has CSS class."""
        return True if self.__widget_context.has_class(css_class) else False

    def connect(self, *args, **kwargs):
        self.__widget.connect(*args, **kwargs)

    def custom_content(self, widget):
        self.__widget.add(widget)


class Dummy(ButtonFactory):
    button = "dummy"

    def __init__(self):
        super().__init__()


class Default(ButtonFactory):
    button = "gtk_default"

    def __init__(self):
        super().__init__()


class QuickSetting(ButtonFactory):
    button = "quick_setting"

    def __init__(self):
        super().__init__()
        self.show = True


class ConnectToCountry(ButtonFactory):
    button = "connect_country"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.add_class("transparent")
        self.label = "CONNECT"


class ConnectToServer(ButtonFactory):
    button = "connect_server"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.add_class("transparent")
        self.label = "CONNECT"


class DisconnectFromServer(ButtonFactory):
    button = "disconnect"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.add_class("transparent")
        self.label = "DISCONNECT"


class Transparent(ButtonFactory):
    button = "transparent"

    def __init__(self):
        super().__init__()


class Chevron(ButtonFactory):
    button = "chevron"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.align_h = Gtk.Align.END
        self.show = True
        self.add_class("chevron")
        self.add_class("chevron-unfold")


class DialogUpgrade(ButtonFactory):
    button = "dialog_upgrade"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.label = "Upgrade"
        self.show = True
        self.add_class("enabled")


class QuickSettingsUpgrade(ButtonFactory):
    button = "dialog_upgrade"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.CENTER
        self.align_v = Gtk.Align.CENTER
        self.label = "Upgrade"
        self.show = True
        self.add_class("quick-settings")


class DialogClose(ButtonFactory):
    button = "dialog_close"

    def __init__(self):
        super().__init__()
        self.label = "Close"
        self.show = True
        self.add_class("transparent-white")
