from abc import ABCMeta

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from ..abstract_widget_factory import WidgetFactory


class LabelFactory(WidgetFactory, metaclass=ABCMeta):
    """Concrete Label Factory class."""

    concrete_factory = "label"

    def __init__(self, label_text):
        self.__widget = Gtk.Label(label_text)
        self.__widget_context = self.__widget.get_style_context()

    @classmethod
    def factory(cls, widget_name, label_text):
        subclasses_dict = cls._get_subclasses_dict("label")
        return subclasses_dict[widget_name](label_text)

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

    @property
    def justify(self):
        return self.__widget.get_justify()

    @justify.setter
    def justify(self, newvalue):
        self.__widget.set_justify(newvalue)

    @property
    def width_in_chars(self):
        return self.__widget.get_width_chars()

    @width_in_chars.setter
    def width_in_chars(self, newvalue):
        self.__widget.set_width_chars(newvalue)

    @property
    def max_width_in_chars(self):
        return self.__widget.get_max_width_chars()

    @max_width_in_chars.setter
    def max_width_in_chars(self, newvalue):
        self.__widget.set_max_width_chars(newvalue)

    @property
    def line_wrap(self):
        return self.__widget.get_line_wrap()

    @line_wrap.setter
    def line_wrap(self, newvalue):
        self.__widget.set_line_wrap(newvalue)

    def add_class(self, css_class):
        """Add CSS class."""
        self.__widget_context.add_class(css_class)

    def remove_class(self, css_class):
        """Remove CSS class."""
        if self.has_class(css_class):
            self.__widget_context.remvove_class(css_class)

    def has_class(self, css_class):
        """Check if has CSS class."""
        return True if self.__widget_context.has_class(css_class) else False


class DialogUpgrade(LabelFactory):
    """DialogUpgrade class."""
    label = "dialog_upgrade"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.max_width_in_chars = 50
        self.max_width_in_chars = 50
        self.line_wrap = True
        self.show = True
        self.add_class("default-text-color")


class Country(LabelFactory):
    """CountryLabel class."""
    label = "country"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.add_class("country-label")


class Server(LabelFactory):
    """CountryLabel class."""
    label = "server"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.add_class("server-label")


class City(LabelFactory):
    """CountryLabel class."""
    label = "city"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_v = Gtk.Align.CENTER
        self.expand_v = True
        self.show = True
        self.add_class("city-label")
