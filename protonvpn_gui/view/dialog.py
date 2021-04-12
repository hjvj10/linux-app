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

    Dialog object is used to displays a dialog window which is context based.
    """
    __gtype_name__ = "DialogView"

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

    def display_logout_confirmation(self, logout_callback):
        """Display dialog with logout confirmation."""
        self.headerbar_label.set_text("VPN Connection Active")
        top_text = "Logging out of the application will disconnect " \
            "the active VPN connection. Do you want to continue ?"

        content_grid = self.__generate_upgrade_content_grid(top_text)
        bottom_grid = self.__generate_bottom_buttons_grid()
        self.main_button.connect("clicked", self.__logout, logout_callback)
        self.main_button.label = "Continue"
        self.__attach_grids(content_grid, bottom_grid)
        self.present()

    def display_quit_confirmation(self, quit_callback):
        """Display dialog with quit app confirmation."""
        self.headerbar_label.set_text("VPN Connection Active")
        top_text = "Quitting the application will disconnnect " \
            "the active VPN connection. Do you want to continue ?"

        content_grid = self.__generate_upgrade_content_grid(top_text)
        bottom_grid = self.__generate_bottom_buttons_grid()
        self.main_button.connect("clicked", self.__quit, quit_callback)
        self.main_button.label = "Continue"
        self.__attach_grids(content_grid, bottom_grid)
        self.present()

    def display_upgrade(self):
        """Display dialog with upgrade request."""
        self.headerbar_label.set_text("Upgrade required")
        top_text = "You're trying to connect to a server which requires " \
            "a ProtonVPN Plus Subscription or higher." \
            "\n\nTo access more servers in all countries, please " \
            "upgrade your subscription."

        content_grid = self.__generate_upgrade_content_grid(top_text)
        bottom_grid = self.__generate_bottom_buttons_grid()
        self.main_button.connect("clicked", self.__upgrade_account)
        self.main_button.label = "Upgrade"
        self.__attach_grids(content_grid, bottom_grid)
        self.present()

    def __generate_upgrade_content_grid(self, top_text):
        """Generate grid with contextual information."""
        content_grid = WidgetFactory.grid("dialog_content")
        top_label = WidgetFactory.label("dialog_main_text", top_text)
        content_grid.attach(top_label.widget, 0, 0, 1, 1)
        return content_grid

    def __generate_bottom_buttons_grid(self):
        """Generate grid with buttons."""
        bottom_grid = WidgetFactory.grid("dialog_buttons")

        buttons_grid = WidgetFactory.grid("dialog_buttons")
        buttons_grid.add_class("grid-button-spacing")
        buttons_grid.align_h = Gtk.Align.END
        buttons_grid.align_v = Gtk.Align.CENTER
        buttons_grid.expand_h = True
        buttons_grid.column_spacing = 15

        self.main_button = WidgetFactory.button("dialog_main")
        self.cancel_button = WidgetFactory.button("dialog_close")

        buttons_grid.attach(self.cancel_button.widget, 0, 0, 1, 1)
        buttons_grid.attach_next_to(
            self.main_button.widget, self.cancel_button.widget,
            Gtk.PositionType.RIGHT, 1, 1
        )
        bottom_grid.attach(buttons_grid.widget, 0, 0, 1, 1)
        self.cancel_button.connect("clicked", self.__close_dialog)

        return bottom_grid

    def __attach_grids(self, top_content_grid, bottom_button_grid):
        """Attach custom content to dialog content grid."""
        self.dialog_container_grid.attach(top_content_grid.widget, 0, 0, 1, 1)
        self.dialog_container_grid.attach_next_to(
            bottom_button_grid.widget, top_content_grid.widget,
            Gtk.PositionType.BOTTOM, 1, 1
        )

    def __close_dialog(self, cancel_button):
        """Close dialog callback."""
        self.destroy()

    def __upgrade_account(self, main_button):
        """Open window in browser with the specified URI to upgrade account."""
        Gtk.show_uri_on_window(
            None,
            "https://account.protonvpn.com/",
            Gdk.CURRENT_TIME
        )

    def __logout(self, main_button, logout_callback):
        """Call logout callback."""
        logout_callback()

    def __quit(self, main_button, quit_callback):
        """Call logout callback."""
        quit_callback()
