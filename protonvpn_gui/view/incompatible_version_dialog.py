import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ..patterns.factory.abstract_widget_factory import WidgetFactory


def display_dialog():
    window = Gtk.Window()
    grid = WidgetFactory.grid("default")
    label = WidgetFactory.label("default")
    label.content = "Current Gtk version is incompatible with ProtonVPN." \
        "\nPlease upgrade to (or any other derivative from) Ubuntu 20.04\n" \
        "or any other distribution based off Gtk 3.24 or higher."

    window.set_default_size(500, 250)
    window.set_title("Incompatible Gtk version")
    window.add(grid.widget)
    grid.expand_h = True
    grid.expand_v = True
    grid.align_h = Gtk.Align.CENTER
    grid.align_v = Gtk.Align.CENTER
    grid.attach(label.widget)
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
