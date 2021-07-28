import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

from ..abstract_widget_factory import WidgetFactory


class GridFactory(WidgetFactory):
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

    def clear(self):
        """Remove all elements from grid."""

    def attach(self, widget, col=0, row=0, width=1, height=1):
        """Attach widget to grid.

        Args:
            widget (Gtk.Widget)
            col (int): column number to attach widget to
            row (int): row number to attach widget to
            width (int): widget width (default 1)
            height (int): widget height (default 1)

        All grids start counting at 0. To attach a widget to the
        3rd row, then row=2 should be passed.
        """
        self.__widget.attach(
            widget, col, row, width, height
        )

    def attach_right_next_to(
        self, widget_to_attach,
        sibling=None, width=1, height=1
    ):
        self.attach_next_to(
            widget_to_attach,
            sibling,
            Gtk.PositionType.RIGHT,
            width, height
        )

    def attach_left_next_to(
        self, widget_to_attach,
        sibling=None, width=1, height=1
    ):
        self.attach_next_to(
            widget_to_attach,
            sibling,
            Gtk.PositionType.LEFT,
            width, height
        )

    def attach_top_next_to(
        self, widget_to_attach,
        sibling=None, width=1, height=1
    ):
        self.attach_next_to(
            widget_to_attach,
            sibling,
            Gtk.PositionType.TOP,
            width, height
        )

    def attach_bottom_next_to(
        self, widget_to_attach,
        sibling=None, width=1, height=1
    ):
        self.attach_next_to(
            widget_to_attach,
            sibling,
            Gtk.PositionType.BOTTOM,
            width, height
        )

    def attach_next_to(
        self, widget_to_attach,
        sibling, attach_position,
        width, height
    ):
        """Attach widget next to sibling.

        Args:
            widget_to_attach (Gtk.Widget)
            sibling (None|Gtk.Widget)
            attach_position (Gtk.PositionType)
            width (int)
            height (int)

        Note about sibling:

        When sibling is None, the widget is placed in row (for left
        or right placement) or column 0 (for top or bottom placement),
        at the end indicated by side. Attaching widgets labeled [1], [2], [3]
        with sibling == None andside == GTK_POS_LEFT yields a layout of 3[1].
        """
        positions = [
            Gtk.PositionType.BOTTOM, Gtk.PositionType.TOP,
            Gtk.PositionType.LEFT, Gtk.PositionType.RIGHT
        ]
        if attach_position not in positions:
            raise KeyError("The position {} is not supported".format(
                attach_position
            ))

        self.__widget.attach_next_to(
            widget_to_attach, sibling,
            attach_position, width, height
        )

    def remove_row(self, row_number):
        """Remove row from grid based on row_number.

        Args:
            row_number (int)
        """
        self.__widget.remove_row(row_number)

    def remove_col(self, col_number):
        """Remove row from grid based on col_number.

        Args:
            col_number (int)
        """
        self.__widget.remove_column(col_number)

    def get_child_at(self, col=0, row=0):
        """Gets child widget from specified position.

        Args:
            col (int)
            row (int)
        """
        return self.__widget.get_child_at(col, row)


class Dummy(GridFactory):
    grid = "dummy"

    def __init__(self):
        super().__init__()


class Default(GridFactory):
    grid = "default"

    def __init__(self):
        super().__init__()
        self.show = True


class TroubleshootContainer(GridFactory):
    grid = "troubleshoot_container"

    def __init__(self):
        super().__init__()
        self.row_spacing = 20
        self.align_h = Gtk.Align.FILL
        self.show = True


class StreamingIconsContainer(GridFactory):
    grid = "streaming_icons_container"

    def __init__(self):
        super().__init__()
        self.add_class("plus-features")
        self.align_h = Gtk.Align.FILL
        self.show = True


class QuickSettings(GridFactory):
    grid = "container"

    def __init__(self):
        super().__init__()
        self.align_h = Gtk.Align.FILL
        self.align_v = Gtk.Align.FILL
        self.expand_h = True
        self.expand_v = True
        self.show = True
        self.add_class("quick-settings-content")


class QuickSettingsButtons(GridFactory):
    grid = "buttons"

    def __init__(self):
        super().__init__()
        self.align_h = Gtk.Align.FILL
        self.align_v = Gtk.Align.FILL
        self.expand_h = True
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
