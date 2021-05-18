import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

from ..abstract_widget_factory import WidgetFactory


class RevealerFactory(WidgetFactory):
    """Concrete Revealer Factory class."""

    concrete_factory = "revealer"

    def __init__(self):
        self.__widget = Gtk.Revealer()
        self.__widget_context = self.__widget.get_style_context()

    @classmethod
    def factory(cls, widget_name):
        subclasses_dict = cls._get_subclasses_dict("revealer")
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
    def reveal(self):
        """Get reveal property.

        Returns:
            bool:
                True if child is revealed
                False if not
        """
        return self.__widget.get_reveal_child()

    @reveal.setter
    def reveal(self, newvalue):
        """Set reveal property.

        Args:
            newvalue (bool)
        """
        self.__widget.set_reveal_child(newvalue)

    @property
    def transition_type(self):
        """Get transition type property."""
        return self.__widget.get_transition_type()

    @transition_type.setter
    def transition_type(self, newvalue):
        """Set transition type property."""
        self.__widget.set_transition_type(newvalue)

    @property
    def transition_duration(self):
        """Get transition duration property."""
        return self.__widget.get_transition_duration()

    @transition_duration.setter
    def transition_duration(self, newvalue):
        """Set transition duration property."""
        self.__widget.set_transition_duration(newvalue)

    def add_class(self, css_class):
        """Add CSS class."""
        self.__widget_context.add_class(css_class)

    def remove_class(self, css_class):
        """Remove CSS class."""
        if self.has_class(css_class):
            self.__widget_context.remvove_class(css_class)

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

    def add(self, widget):
        """Add widger to reavealer."""
        self.__widget.add(widget)


class ServerList(RevealerFactory):
    revealer = "server_list"

    def __init__(self):
        super().__init__()
        self.expand_h = True
        self.expand_v = False
        self.align_v = Gtk.Align.FILL
        self.reveal = False
        self.transition_type = Gtk\
            .RevealerTransitionType.SLIDE_DOWN
        self.show = True
