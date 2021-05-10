import os

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk

from ..constants import CSS_DIR_PATH, UI_DIR_PATH, protonvpn_logo
from ..patterns.factory import WidgetFactory
from ..constants import APP_VERSION
from protonvpn_nm_lib.constants import APP_VERSION as lib_version
from proton.constants import VERSION as api_version


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "dialog.ui"))
class DialogView(Gtk.ApplicationWindow):
    """
    Dialog view. GTK Composite object.

    Dialog object as composite to displays a dialog window which is context based.
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
        self.content_label = WidgetFactory.label("dialog_main_text")

        self.__generate_content_grid()
        self.__generate_bottom_buttons_grid()
        self.__attach_grids()

        protonvpn_headerbar_pixbuf = self.dummy_object\
            .create_icon_pixbuf_from_name(
                "protonvpn-sign-green.svg",
                width=50, height=50,
            )
        window_icon = self.dummy_object.create_icon_pixbuf_from_name(
            protonvpn_logo
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

    def display_dialog(self):
        """Displays the dialog to the user."""
        self.present()

    def close_dialog(self, cancel_button=None):
        """Closes and destroys the dialog."""
        self.destroy()

    def add_extra_content(self, widget):
        """Add extra content to window.

        Args:
            widget: should be a container (GTK.Grid or Gtk.Box)
        """
        self.__content_grid.attach_bottom_next_to(
            widget,
            self.content_label.widget
        )

    def __generate_content_grid(self):
        """Generate grid with contextual information."""
        self.__content_grid = WidgetFactory.grid("dialog_content")
        self.__content_grid.attach(self.content_label.widget, 0, 0, 1, 1)

    def __generate_bottom_buttons_grid(self):
        """Generate grid with buttons."""
        self.__bottom_grid = WidgetFactory.grid("dialog_buttons")

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
        self.__bottom_grid.attach(buttons_grid.widget, 0, 0, 1, 1)
        self.cancel_button.connect("clicked", self.close_dialog)

    def __attach_grids(self):
        """Attach custom content to dialog content grid."""
        self.dialog_container_grid.attach(self.__content_grid.widget, 0, 0, 1, 1)
        self.dialog_container_grid.attach_next_to(
            self.__bottom_grid.widget, self.__content_grid.widget,
            Gtk.PositionType.BOTTOM, 1, 1
        )

    @property
    def buttons_visible(self):
        return self.__bottom_grid.show

    @buttons_visible.setter
    def buttons_visible(self, newvalue):
        self.__bottom_grid.show = newvalue


class LoginKillSwitchDialog:
    """Login Kill Switch Dialog.

    Is displayed when the users clicks on disable button on login
    screen. The button that displays this dialog will only appear
    if the user is not logged in and the kill switch is detected as enabled.
    """
    def __init__(
        self, application, login_view_model, callback_func=None
    ):
        self.login_view_model = login_view_model
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("Disable Kill Switch")
        self.dialog_view.content_label.content = "Permanent Kill Switch is " \
            "blocking any outgoing connection and preventing " \
            "your IP to be exposed.\n\n" \
            "Do you want to disable Kill Switch ?"

        self.dialog_view.main_button.connect(
            "clicked", self._disable_killswitch,
            callback_func, application
        )
        self.dialog_view.main_button.label = "Disable"
        self.dialog_view.display_dialog()

    def _disable_killswitch(self, continue_button, callback_func, application):
        self.login_view_model.disable_killswitch()
        callback_func()
        self.dialog_view.close_dialog()


class ConnectUpgradeDialog:
    """Connect Upgrade Dialog.

    Is displayed when the users clicks on upgrade button on server
    objects. The button that displays this dialog will only appear
    if the the server tier is higher when compared to users tier.
    """
    def __init__(self, application, callback_func=None):
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("Upgrade required")
        self.dialog_view.content_label.content = "You're trying to connect " \
            "to a server which requires " \
            "a ProtonVPN Plus Subscription or higher." \
            "\n\nTo access more servers in all countries, please " \
            "upgrade your subscription."

        self.dialog_view.main_button.connect(
            "clicked", self._upgrade_account, callback_func
        )
        self.dialog_view.main_button.label = "Upgrade"
        self.dialog_view.display_dialog()

    def _upgrade_account(self, main_button, callback_func):
        """Open window in browser with the specified URI to upgrade account."""
        Gtk.show_uri_on_window(
            None,
            "https://account.protonvpn.com/",
            Gdk.CURRENT_TIME
        )
        self.dialog_view.close_dialog()


class LogoutDialog:
    """Logout Dialog.

    Is displayed when the users clicks on logout button.
    """
    def __init__(self, application, callback_func=None):
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("VPN Connection Active")
        self.dialog_view.content_label.content = "Logging out of the " \
            "application will disconnect the active VPN connection.\n\n" \
            "Do you want to continue ?"

        self.dialog_view.main_button.connect(
            "clicked", self._logout, callback_func
        )
        self.dialog_view.main_button.label = "Continue"
        self.dialog_view.display_dialog()

    def _logout(self, main_button, callback_func):
        """Call logout callback."""
        callback_func()


class QuitDialog:
    """Quit Dialog.

    Is displayed when the users clicks on quit button.
    """
    def __init__(self, application, callback_func=None):
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("VPN Connection Active")
        self.dialog_view.content_label.content = "Quitting the application " \
            "will disconnnect the active VPN connection.\n\n" \
            "Do you want to continue ?"

        self.dialog_view.main_button.connect(
            "clicked", self._quit, callback_func
        )
        self.dialog_view.main_button.label = "Continue"
        self.dialog_view.display_dialog()

    def _quit(self, main_button, callback_func):
        """Call logout callback."""
        callback_func()


class AboutDialog:
    """About Dialog.

    Is displayed when the users clicks on logout button.
    """
    def __init__(self, application, callback_func=None):
        self.dialog_view = DialogView(application)
        self.dialog_view.headerbar_label.set_text("About")
        app_version = "ProtonVPN: \tv{} (library: v{} / api-client: v{})".format(
            APP_VERSION, lib_version, api_version
        )
        self.dialog_view.content_label.align_h = Gtk.Align.START
        self.dialog_view.content_label.ident_h = 0
        self.dialog_view.content_label.content = app_version
        self.dialog_view.buttons_visible = False
        additional_context = WidgetFactory.grid("default")
        import datetime
        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()
        copyright_label = WidgetFactory.label(
            "default", "Copyright Proton Technologies AG {}".format(date.strftime("%Y"))
        )
        copyright_label.add_class("dark-text-color")
        copyright_label.add_class("font-small")
        additional_context.attach(copyright_label.widget)
        additional_context.ident_h = 0
        additional_context.ident_v = 0
        copyright_label.ident_h = 0
        copyright_label.ident_v = 0
        self.dialog_view.add_extra_content(additional_context.widget)

        self.dialog_view.display_dialog()
