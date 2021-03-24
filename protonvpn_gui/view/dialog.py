import os

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk

from ..constants import CSS_DIR_PATH, UI_DIR_PATH
from ..factory import WidgetFactory


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "dialog.ui"))
class DialogView(Gtk.ApplicationWindow):
    """
    Dialog view. GTK Composite object.
    """
    __gtype_name__ = 'DialogView'

    # Labels
    headerbar_label = Gtk.Template.Child()

    # Images/Icons
    headerbar_sign_icon = Gtk.Template.Child()

    # Containers
    dialog_container_grid = Gtk.Template.Child()

    def __init__(self, application):
        super().__init__(application=application)
        self.dummy_object = WidgetFactory.image("dummy")
        protonvpn_headerbar_pixbuf = self.dummy_object\
            .create_icon_pixbuf_from_name(
                "protonvpn-sign-green.svg",
                width=50, height=50,
            )
        window_icon = self.dummy_object.create_icon_pixbuf_from_name(
            "protonvpn_logo.png",
        )
        self.headerbar_sign_icon.set_from_pixbuf(protonvpn_headerbar_pixbuf)
        self.set_icon(window_icon)
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(
            os.path.join(CSS_DIR_PATH, "dialog.css")
        )
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def display_upgrade(self):
        self.headerbar_label.set_text("Upgrade required")
        content_grid = self.__generate_upgrade_content_grid()
        bottom_grid = self.__generate_upgrade_bottom_grid()

        self.dialog_container_grid.attach(content_grid.widget, 0, 0, 1, 1)
        self.dialog_container_grid.attach_next_to(
            bottom_grid.widget, content_grid.widget,
            Gtk.PositionType.BOTTOM, 1, 1
        )

        self.present()

    def __generate_upgrade_content_grid(self):
        top_text = "You're trying to connect to a server which requires " \
            "a ProtonVPN Plus Subscription or higher." \
            "\n\nTo access more servers in all countries, please " \
            "upgrade your subscription."

        content_grid = WidgetFactory.grid("dialog_content")
        top_label = WidgetFactory.label("dialog_upgrade", top_text)

        content_grid.attach(top_label.widget, 0, 0, 1, 1)

        return content_grid

    def __generate_upgrade_bottom_grid(self):
        bottom_grid = WidgetFactory.grid("dialog_buttons")

        buttons_grid = WidgetFactory.grid("dialog_buttons")
        buttons_grid.add_class("grid-button-spacing")
        buttons_grid.align_h = Gtk.Align.END
        buttons_grid.align_v = Gtk.Align.CENTER
        buttons_grid.expand_h = True
        buttons_grid.column_spacing = 15

        upgrade_button = WidgetFactory.button("dialog_upgrade")
        cancel_button = WidgetFactory.button("dialog_close")

        buttons_grid.attach(cancel_button.widget, 0, 0, 1, 1)
        buttons_grid.attach_next_to(
            upgrade_button.widget, cancel_button.widget,
            Gtk.PositionType.RIGHT, 1, 1
        )
        bottom_grid.attach(buttons_grid.widget, 0, 0, 1, 1)
        upgrade_button.connect("clicked", self.__upgrade_account)
        cancel_button.connect("clicked", self.__close_dialog)

        return bottom_grid

    def __close_dialog(self, cancel_button):
        self.destroy()

    def __upgrade_account(self, upgrade_button):
        Gtk.show_uri_on_window(
            None,
            "https://account.protonvpn.com/",
            Gdk.CURRENT_TIME
        )
