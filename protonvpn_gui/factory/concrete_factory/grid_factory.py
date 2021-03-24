from abc import ABCMeta

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

from ..abstract_widget_factory import WidgetFactory


class GridFactory(WidgetFactory, metaclass=ABCMeta):
    """Concrete Grid Factory class."""

    concrete_factory = "grid"

    def __init__(self):
        self.__widget = Gtk.Grid()
        self.__widget_context = self.__widget.get_style_context()

    @classmethod
    def factory(cls, widget_name):
        subclasses_dict = cls._get_subclasses_dict("grid")
        return subclasses_dict[widget_name]()

    @property
    def widget(self):
        """Get widget object."""
        return self.__widget

    @property
    def context(self):
        return self.__widget_context

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
    def tooltip(self):
        return self.__widget.get_propert("has-tooltip")

    @tooltip.setter
    def tooltip(self, newvalue):
        self.__widget.set_property("has-tooltip", newvalue)

    @property
    def row_spacing(self):
        return self.__widget.get_row_spacing()

    @row_spacing.setter
    def row_spacing(self, newvalue):
        self.__widget.set_row_spacing(newvalue)

    @property
    def column_spacing(self):
        return self.__widget.get_column_spacing()

    @column_spacing.setter
    def column_spacing(self, newvalue):
        self.__widget.set_column_spacing(newvalue)

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

    def connect(self, *args, **kwargs):
        self.__widget.connect(*args, **kwargs)

    def attach(self, *args, **kwargs):
        self.__widget.attach(*args, **kwargs)

    def attach_next_to(self, *args, **kwargs):
        self.__widget.attach_next_to(*args, **kwargs)


class Default(GridFactory):
    grid = "default"

    def __init__(self):
        super().__init__()
        self.show = True


class DialogContent(GridFactory):
    grid = "dialog_content"

    def __init__(self):
        super().__init__()
        self.align_h = Gtk.Align.START
        self.align_v = Gtk.Align.FILL
        self.expand_v = True
        self.row_spacing = 20
        self.expand_h = False
        self.add_class("grid-spacing")
        self.show = True


class DialogButtons(GridFactory):
    grid = "dialog_buttons"

    def __init__(self):
        super().__init__()
        self.align_h = Gtk.Align.FILL
        self.align_v = Gtk.Align.END
        self.expand_h = True
        self.show = True


class MainCountryRow(GridFactory):
    grid = "country_row"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_v = Gtk.Align.FILL
        self.show = True
        self.add_class("country-row")


class CountryRowLeftChild(GridFactory):
    grid = "left_child_in_country_row"

    def __init__(self):
        super().__init__()
        self.expand_h = False
        self.align_h = Gtk.Align.START
        self.align_v = Gtk.Align.CENTER
        self.show = True


class CountryRowRightChild(GridFactory):
    grid = "right_child_in_country_row"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.show = True
        # self.add_class("test-class5")


class ServerRow(GridFactory):
    grid = "server_row"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_v = Gtk.Align.FILL
        self.expand_v = True
        self.show = True
        self.add_class("server-row")


class ServerRowLeftChild(GridFactory):
    grid = "left_child_in_server_row"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.align_h = Gtk.Align.START
        self.show = True
        # self.add_class("test-class3")


class ServerRowRightChild(GridFactory):
    grid = "right_child_in_server_row"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.align_h = Gtk.Align.END
        self.show = True
        # self.add_class("test-class")


class RevealerChild(GridFactory):
    grid = "revealer_child"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_v = Gtk.Align.FILL
        self.show = True
        # self.add_class("test-class2")
