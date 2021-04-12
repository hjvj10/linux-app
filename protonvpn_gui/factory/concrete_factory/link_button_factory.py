import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from ..abstract_button_factory import AbstractButtonFactory


class LinkButtonFactory(AbstractButtonFactory):
    """Concrete Button Factory class."""

    concrete_factory = "link_button"

    def __init__(self):
        self.__widget = Gtk.LinkButton(uri="", label="")
        self.__widget_context = self.__widget.get_style_context()

    @classmethod
    def factory(cls, widget_name):
        subclasses_dict = cls._get_subclasses_dict("link")
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
    def url(self):
        return self.__widget.get_uri()

    @url.setter
    def url(self, newvalue):
        return self.__widget.set_uri(newvalue)

    @property
    def ident_h(self):
        """Get vertical align."""
        pass
        # return self.__widget.label.get_xalign()

    @ident_h.setter
    def ident_h(self, newvalue):
        """Set vertical align."""
        pass
        # return self.__widget.label.set_xalign(float(newvalue))

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


class Dummy(LinkButtonFactory):
    link = "dummy_link"

    def __init__(self):
        super().__init__()


class LearnMore(LinkButtonFactory):
    link = "learn_more"

    def __init__(self):
        super().__init__()
        self.add_class("view-more")
        self.show = True
        self.align_h = Gtk.Align.START
        self.ident_h = 0
