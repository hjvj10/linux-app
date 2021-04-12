import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango
from ..abstract_widget_factory import WidgetFactory


class TextViewFactory(WidgetFactory):
    """Concrete Button Factory class.
    A textview can be used instead of a label where
    there is multiple lines to displays or edit.
    """

    concrete_factory = "textview"

    def __init__(self, text):
        self.__textbuffer = Gtk.TextBuffer()
        self.__tag_link = self.__textbuffer.create_tag(
            "bold", weight=Pango.Weight.BOLD
        )
        self.__textbuffer.set_text(text)
        self.__widget = Gtk.TextView(buffer=self.__textbuffer)
        self.__widget_context = self.__widget.get_style_context()

    @classmethod
    def factory(cls, widget_name, text):
        subclasses_dict = cls._get_subclasses_dict("textview")
        return subclasses_dict[widget_name](text)

    @property
    def widget(self):
        """Get widget object."""
        return self.__widget

    @property
    def context(self):
        return self.__widget_context

    @property
    def text(self):
        """Get widget text."""
        return self.__textbuffer.get_text(
            self.__textbuffer.get_start_iter(),
            self.__textbuffer.get_end_iter(),
            self.__textbuffer
        )

    @text.setter
    def text(self, newvalue):
        """Set widget text.

        Args:
            newvalue (string)
        """
        self.__textbuffer.set_text(newvalue)

    def insert_link_at_end(self, string):
        end_iter = self.__textbuffer.get_end_iter()
        self.__textbuffer.insert(end_iter, string)
        new_end_iter = self.__textbuffer.get_end_iter()
        self.__textbuffer.apply_tag(self.__tag_link, end_iter, new_end_iter)

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

    # @property
    # def ident_h(self):
    #     """Get vertical align."""
    #     return self.__widget.get_xalign()

    # @ident_h.setter
    # def ident_h(self, newvalue):
    #     """Set vertical align."""
    #     return self.__widget.set_xalign(float(newvalue))

    @property
    def justify(self):
        return self.__widget.get_justify()

    @justify.setter
    def justify(self, newvalue):
        self.__widget.set_justify(newvalue)

    # @property
    # def width_in_chars(self):
    #     return self.__widget.get_width_chars()

    # @width_in_chars.setter
    # def width_in_chars(self, newvalue):
    #     self.__widget.set_width_chars(newvalue)

    # @property
    # def max_width_in_chars(self):
    #     return self.__widget.get_max_width_chars()

    # @max_width_in_chars.setter
    # def max_width_in_chars(self, newvalue):
    #     self.__widget.set_max_width_chars(newvalue)

    @property
    def line_wrap(self):
        return self.__widget.get_wrap_mode()

    @line_wrap.setter
    def line_wrap(self, newvalue):
        wrap_dict = {
            "none": Gtk.WrapMode(0),
            "char": Gtk.WrapMode(1),
            "word": Gtk.WrapMode(2),
            "word_char": Gtk.WrapMode(3),
        }
        if newvalue not in wrap_dict:
            raise NotImplementedError("Wrap mode not supported")

        self.__widget.set_wrap_mode(wrap_dict[newvalue])

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


class Dummy(TextViewFactory):
    textview = "dummy_textview"

    def __init__(self, text):
        super().__init__(text)


class QuickSettingDescription(TextViewFactory):
    textview = "quick_setting_description"

    def __init__(self, text):
        super().__init__(text)
        self.align_h = Gtk.Align.START
        self.expand_h = True
        self.align_v = Gtk.Align.FILL
        self.line_wrap = "word"
        self.show = True
        self.add_class("quick-settings-description")
        self.add_class("default-text-color")
