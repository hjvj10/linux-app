import os

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio

from ..constants import UI_DIR_PATH
from ..patterns.factory import WidgetFactory
from .dialog import WebView


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "human_verification.ui"))
class HumanVerificationView(Gtk.ApplicationWindow):
    """
    Human Verification view. GTK Composite object.

    Currently not used, but will be incorporated in future.
    """
    __gtype_name__ = "HumanVerificationView"

    MAIN_STACK = "main_page"
    SMS_STACK = "sms"
    EMAIL_STACK = "email"
    CAPTCHA_STACK = "captcha"

    # Grid
    email_back_button_grid = Gtk.Template.Child()
    sms_back_button_grid = Gtk.Template.Child()

    # Button
    confirm_email_button = Gtk.Template.Child()
    confirm_sms_button = Gtk.Template.Child()

    # Label
    human_verification_info_label = Gtk.Template.Child()

    # Other
    verification_stack = Gtk.Template.Child()

    def __init__(self, application):
        super().__init__(application=application)
        self.__setup_actions()
        self.__generate_back_buttons()
        self.webview = WebView(application)
        self.__url = None
        self.human_verification_info_label.set_text(
            "Please select a method to complete human verification."
        )

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, newvalue):
        self.__url = newvalue

    def show_child(self, action, cancellable, stack_to_display):
        if not stack_to_display == self.CAPTCHA_STACK:
            self.verification_stack.props.visible_child_name = stack_to_display
            return

        if not self.__url:  # or regex pattern
            # TO-DO: Raise exception
            pass

        self.webview.display(self.__url)

    def __generate_back_buttons(self):
        """Generate back buttons that return to main stack."""
        back_button_grids = [
            self.email_back_button_grid,
            self.sms_back_button_grid,
        ]

        for i in range(0, len(back_button_grids)):
            back_button = WidgetFactory.button("default")
            back_button.connect("clicked", self.show_child, "None", self.MAIN_STACK)
            back_button.show = True
            try:
                back_button_grids[i].attach(back_button.widget, 0, 0, 1, 1)
            except IndexError:
                pass

    def confirm_verification(self, gio_action, cancellable, type_of_confirmation):
        """Confirm human verification.

        Usually only email or sms methods would use this method.

        Args:
            gtk_action (Gio.SimpleAction): the action that invoked this method
            cancellable (None): if the action is cancellable
            type_of_confirmation (string): either `sms` or `email`
        """
        # TO-DO
        pass

    def __setup_actions(self):
        """Setup actions.

        From documentation:
            Actions represent operations that the user
            can perform, along with some information on
            how it should be presented in the interface.
            Each action provides methods to create icons,
            menu items and toolbar items representing itself.
        (https://developer.gnome.org/gtk3/unstable/GtkAction.html)

        Actions can be mapped to a certain user action (event), instead
        of directly mapping event handlers. Should be used when possible
        to keep UI code portable.
        """
        # logger.info("Setting up actions")

        # create action
        confirm_email_action = Gio.SimpleAction.new("confirm_email", None)
        confirm_sms_action = Gio.SimpleAction.new("confirm_sms", None)
        display_captcha_action = Gio.SimpleAction.new("display_captcha", None)
        display_sms_action = Gio.SimpleAction.new("display_sms", None)
        display_email_action = Gio.SimpleAction.new("display_email", None)

        # connect action to callback
        confirm_email_action.connect("activate", self.confirm_verification, self.EMAIL_STACK)
        confirm_sms_action.connect("activate", self.confirm_verification, self.SMS_STACK)

        display_captcha_action.connect("activate", self.show_child, self.CAPTCHA_STACK)
        display_sms_action.connect("activate", self.show_child, self.SMS_STACK)
        display_email_action.connect("activate", self.show_child, self.EMAIL_STACK)

        # add action
        self.add_action(confirm_email_action)
        self.add_action(confirm_sms_action)

        self.add_action(display_captcha_action)
        self.add_action(display_email_action)
        self.add_action(display_sms_action)
