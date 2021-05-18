import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from ..abstract_button_factory import AbstractButtonFactory


class ButtonFactory(AbstractButtonFactory):
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

    def remove_all_classes(self):
        css_list = self.__widget_context.list_classes()
        for css_class in css_list:
            self.__widget_context.remove_class(css_class)

    def replace_all_by(self, css_class):
        self.remove_all_classes()
        self.add_class(css_class)

    def replace_old_class_with_new_class(self, old_classes, new_classes):
        """Replaces old_classes with new_classes.

        Args:
            old_classes (str|list)
            new_classes (str|list)
        """
        def worker(css_class):
            if isinstance(css_class, list):
                for class_ in css_class:
                    self.remove_class(class_)
            elif isinstance(css_class, str):
                self.remove_class(css_class)
            else:
                raise TypeError(
                    "Unexpected type (list or str expected, but got {})".format( # noqa
                        type(css_class)
                    )
                )
        worker(old_classes)
        worker(new_classes)

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


class HeaderInfo(ButtonFactory):
    button = "header_info"

    def __init__(self):
        super().__init__()
        self.expand_h = False
        self.show = True


class QuickSetting(ButtonFactory):
    button = "quick_setting"

    def __init__(self):
        super().__init__()
        self.show = True


class QuickSettingsUpgrade(ButtonFactory):
    button = "quick_settings_upgrade"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.CENTER
        self.align_v = Gtk.Align.CENTER
        self.label = "Upgrade"
        self.show = True
        self.add_class("quick-settings")


class ConnectToCountry(ButtonFactory):
    button = "connect_country"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.add_class("transparent")
        self.label = "CONNECT"
        self.show = False


class ConnectToServer(ButtonFactory):
    button = "connect_server"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.add_class("transparent")
        self.label = "CONNECT"
        self.show = False


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


class DialogMain(ButtonFactory):
    button = "dialog_main"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.add_class("enabled")


class DialogClose(ButtonFactory):
    button = "dialog_close"

    def __init__(self):
        super().__init__()
        self.label = "Close"
        self.show = True
        self.add_class("transparent-white")
