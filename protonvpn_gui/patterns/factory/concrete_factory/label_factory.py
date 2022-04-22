import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango
from ..abstract_widget_factory import WidgetFactory


class LabelFactory(WidgetFactory):
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

    def set_content_with_markup(self, str):
        self.__widget.set_markup(str)

    @property
    def content(self):
        """Get widget label."""
        return self.__widget.props.label

    @content.setter
    def content(self, newvalue):
        """Set widget label.

        Args:
            newvalue (string)
        """
        self.__widget.props.label = newvalue

    @property
    def show(self):
        """Get widget visibility.

        Returns:
            bool
        """
        return self.__widget.get_visible()

    @show.setter
    def show(self, newvalue):
        """Set widget visibiltiy."""
        self.__widget.set_visible(newvalue)

    @property
    def can_be_selected(self):
        """Gets the value set by set_selectable().

        Returns:
            bool
        """
        return self.__widget.get_selectable()

    @can_be_selected.setter
    def can_be_selected(self, newvalue):
        """Set widget visibiltiy."""
        self.__widget.set_selectable(newvalue)

    @property
    def can_focus(self):
        """Determines whether widget can own the input focus.

        Returns:
            bool
        """
        return self.__widget.get_can_focus()

    @can_focus.setter
    def can_focus(self, newvalue):
        """Set whether widget can own the input focus.

        See Gtk.Widget:grab_focus() for actually setting the input focus on a widget.
        """
        self.__widget.set_can_focus(newvalue)

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
    def ident_h(self):
        """Get vertical align."""
        return self.__widget.get_xalign()

    @ident_h.setter
    def ident_h(self, newvalue):
        """Set vertical align."""
        return self.__widget.set_xalign(float(newvalue))

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
        if not self.line_wrap:
            self.line_wrap = True
        self.__widget.set_width_chars(newvalue)

    @property
    def max_width_in_chars(self):
        return self.__widget.get_max_width_chars()

    @max_width_in_chars.setter
    def max_width_in_chars(self, newvalue):
        if not self.line_wrap:
            self.line_wrap = True
        self.__widget.set_max_width_chars(newvalue)

    @property
    def line_wrap(self):
        return self.__widget.get_line_wrap()

    @line_wrap.setter
    def line_wrap(self, newvalue):
        self.__widget.set_line_wrap(newvalue)

    @property
    def wrap_mode(self):
        return self.__widget.get_line_wrap_mode()

    @wrap_mode.setter
    def wrap_mode(self, newvalue):
        if not self.line_wrap:
            self.line_wrap = True
        return self.__widget.set_line_wrap_mode(newvalue)

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


class Default(LabelFactory):
    """Default class."""
    label = "default"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.add_class("text-normal")


class ServerListHeader(LabelFactory):
    """ServerListHeader class."""
    label = "server_list_header"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.add_class("text-hint")


class GenericEventIncentive(LabelFactory):
    """Default class."""
    label = "generic_event_incentive"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.CENTER
        self.align_v = Gtk.Align.CENTER
        self.justify = Gtk.Justification.CENTER
        self.expand_h = True
        self.show = True
        self.add_class("text-normal")
        self.line_wrap = True
        _max_char_width = 45
        self.width_in_chars = _max_char_width
        self.max_width_in_chars = _max_char_width
        # WORD
        # CHAR
        # WORD_CHAR
        self.wrap_mode = Pango.WrapMode.WORD


class GenericEventSaveUpTo(LabelFactory):
    """Default class."""
    label = "generic_event_save_up_to"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.CENTER
        self.align_v = Gtk.Align.CENTER
        self.expand_h = True
        self.show = True
        self.add_class("generic-event-save-up-to")


class GenericEventTitle(LabelFactory):
    """Default class."""
    label = "generic_event_title"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.FILL
        self.align_v = Gtk.Align.CENTER
        self.expand_h = True
        self.show = True
        self.add_class("margin-bottom-10px")
        self.add_class("text-normal")


class GenericEventFooter(LabelFactory):
    """Default class."""
    label = "generic_event_footer"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.FILL
        self.align_v = Gtk.Align.CENTER
        self.expand_h = True
        self.show = True
        self.add_class("text-weak")
        self.add_class("margin-top-10px")


class TroubleshootDescription(LabelFactory):
    """TroubleshootDescription class."""
    label = "troubleshoot_description"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.justify = Gtk.Justification.FILL
        self.align_h = Gtk.Align.FILL
        self.expand_h = True
        self.show = True
        self.add_class("text-weak")
        self.add_class("quick-settings-title")
        self.line_wrap = True
        self.ident_h = 0
        self.width_in_chars = 60
        self.max_width_in_chars = 60
        # WORD
        # CHAR
        # WORD_CHAR
        self.wrap_mode = Pango.WrapMode.WORD


class TroubleshootTitle(LabelFactory):
    """TroubleshootTitle class."""
    label = "troubleshoot_title"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.ident_h = 0
        self.add_class("bold")
        self.add_class("text-normal")


class PremiumFeaturesPopoverTitle(LabelFactory):
    """PremiumFeaturesPopoverTitle class."""
    label = "premium_features_popover_title"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.add_class("text-normal")
        self.add_class("quick-settings-title")
        self.add_class("margin-left-10px")
        self.add_class("bold")


class PremiumFeaturesPopoverDescription(LabelFactory):
    """PremiumFeaturesPopoverTitle class."""
    label = "premium_features_popover_description"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.add_class("text-weak")
        self.add_class("quick-settings-title")
        self.add_class("margin-left-10px")
        self.line_wrap = True
        self.ident_h = 0
        self.width_in_chars = 40
        self.max_width_in_chars = 40
        # Word
        # Char
        # WordChar
        self.wrap_mode = Pango.WrapMode.WORD_CHAR


class PremiumFeaturesPopoverChip(LabelFactory):
    """PremiumFeaturesPopoverChip class."""
    label = "premium_features_popover_chip"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.add_class("chip-tier")
        self.show = True


class StreamingDescription(LabelFactory):
    """PremiumFeaturesPopoverTitle class."""
    label = "streaming_description"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.justify = Gtk.Justification.FILL
        self.align_h = Gtk.Align.FILL
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.add_class("text-weak")
        self.add_class("quick-settings-title")
        self.add_class("margin-left-10px")
        self.line_wrap = True
        self.ident_h = 0
        self.width_in_chars = 40
        self.max_width_in_chars = 40
        # Word
        # Char
        # WordChar
        self.wrap_mode = Pango.WrapMode.WORD_CHAR


class StreamingTitle(LabelFactory):
    """StreamingTitle class."""
    label = "streaming_title"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.CENTER
        self.justify = Gtk.Justification.CENTER
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.width_in_chars = 10
        self.max_width_in_chars = 10
        self.add_class("bold")
        self.add_class("text-normal")


class QuickSettingsTitle(LabelFactory):
    """QuickSettingsTitle class."""
    label = "quick_settings_title"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.expand_h = True
        self.align_v = Gtk.Align.CENTER
        self.show = True
        self.add_class("text-normal")
        self.add_class("quick-settings-title")


class QuickSettingsDescription(LabelFactory):
    """QuickSettingsDescription class."""
    label = "quick_settings_description"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.expand_h = True
        self.align_v = Gtk.Align.FILL
        self.width_in_chars = 37
        self.max_width_in_chars = 37
        self.ident_h = 0
        self.line_wrap = True
        self.show = True
        self.add_class("text-normal")
        self.add_class("quick-settings-description")


class QuickSettingsFootnote(LabelFactory):
    """QuickSettingsDescription class."""
    label = "quick_settings_footnote"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.expand_h = True
        self.align_v = Gtk.Align.END
        self.expand_v = True
        self.show = True
        self.add_class("quick-settings-footnote")


class QuickSettingsButton(LabelFactory):
    """QuickSettingsDescription class."""
    label = "quick_settings_button"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.expand_h = True
        self.width_in_chars = 20
        self.max_width_in_chars = 20
        self.line_wrap = True
        self.ident_h = 0
        self.align_v = Gtk.Align.CENTER
        self.add_class("padding-y-10px")
        self.add_class("padding-x-5px")
        self.show = True


class QuickSettingsButtonUpgrade(LabelFactory):
    """QuickSettingsDescription class."""
    label = "quick_settings_upgrade_in_button"

    def __init__(self, label_text):
        if not label_text:
            label_text = "Plus"
        super().__init__(label_text)
        self.expand_h = False
        self.align_h = Gtk.Align.END
        self.align_v = Gtk.Align.CENTER
        self.add_class("upgrade-in-button")
        self.show = True


class DialogUpgrade(LabelFactory):
    """DialogUpgrade class."""
    label = "dialog_main_text"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.START
        self.width_in_chars = 50
        self.max_width_in_chars = 50
        self.line_wrap = True
        self.show = True
        self.add_class("text-normal")
        self.add_class("font-large")


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


class NewBrandTitle(LabelFactory):
    label = "new-brand-title"

    def __init__(self, label_text):
        super().__init__(label_text)
        self.align_h = Gtk.Align.CENTER
        self.line_wrap = True
        self.show = True
        self.add_class("text-normal")
        self.add_class("font-xx-large")
        self.add_class("font-bold")
        self.add_class("margin-bottom-10px")
