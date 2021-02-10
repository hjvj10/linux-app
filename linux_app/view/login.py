import os

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, GdkPixbuf, Gio, Gtk

from ..constants import CSS_DIR_PATH, ICON_DIR_PATH, IMG_DIR_PATH, UI_DIR_PATH
import threading


@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "login.ui"))
class LoginView(Gtk.ApplicationWindow):
    __gtype_name__ = 'LoginView'

    proton_username_entry = Gtk.Template.Child()
    proton_password_entry = Gtk.Template.Child()
    login_button = Gtk.Template.Child()
    img_protonvpn_logo = Gtk.Template.Child()
    popover_login_menu = Gtk.Template.Child()
    banner_error_label = Gtk.Template.Child()
    overlay_box = Gtk.Template.Child()
    overlay_logo_image = Gtk.Template.Child()
    overlay_bottom_label = Gtk.Template.Child()
    top_banner_revealer = Gtk.Template.Child()
    top_banner_revealer_grid = Gtk.Template.Child()
    overlay_spinner = Gtk.Template.Child()

    icon_width = 18
    icon_heigt = 18

    def __init__(self, **kwargs):
        self.login_presenter = kwargs.pop("presenter")
        self.dashboard_window = kwargs.pop("dashboard_window")
        super().__init__(**kwargs)
        self.setup_images()
        self.setup_css()
        self.setup_actions()
        self.top_banner_revealer_grid_context = self.top_banner_revealer_grid.get_style_context()  # noqa
        self.proton_username_entry.connect("changed", self.on_entry_changed)
        self.proton_password_entry.connect("changed", self.on_entry_changed)
        self.login_presenter.login_view = self
        self.overlay_spinner.set_property("width-request", 200)
        self.overlay_spinner.set_property("height-request", 200)

    def on_entry_changed(self, gtk_entry_object):
        gtk_entry_objects = [
            self.proton_username_entry,
            self.proton_password_entry
        ]
        string_min_length = 5

        try:
            index = gtk_entry_objects.index(gtk_entry_object)
        except KeyError:
            return

        _ = gtk_entry_objects.pop(index)
        second_entry_object = gtk_entry_objects.pop()

        self.login_button.set_property("sensitive", False)
        self.set_css_class(self.login_button, "disabled", "enabled")

        if not len(gtk_entry_object.get_text().strip()) > string_min_length:
            return

        if len(second_entry_object.get_text().strip()) > string_min_length:
            self.login_button.set_property("sensitive", True)
            self.set_css_class(self.login_button, "enabled", "disabled")
        else:
            self.set_css_class(self.login_button, "disabled", "enabled")
            self.login_button.set_property("sensitive", False)

    def setup_images(self):
        self.password_show_entry_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale( # noqa
            filename=os.path.join(
                ICON_DIR_PATH,
                "eye-show.imageset/eye-show@3x.png",

            ),
            width=self.icon_width,
            height=self.icon_heigt,
            preserve_aspect_ratio=True
        )
        self.password_hide_entry_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale( # noqa
            filename=os.path.join(
                ICON_DIR_PATH,
                "eye-hide.imageset/eye-hide@3x.png",

            ),
            width=self.icon_width,
            height=self.icon_heigt,
            preserve_aspect_ratio=True
        )

        logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(
                IMG_DIR_PATH,
                "protonvpn-logo-white.svg"
            ),
            width=325,
            height=250,
            preserve_aspect_ratio=True
        )

        self.img_protonvpn_logo.set_from_pixbuf(logo_pixbuf)
        self.overlay_logo_image.set_from_pixbuf(logo_pixbuf)
        self.proton_password_entry.set_icon_from_pixbuf(
            Gtk.EntryIconPosition.SECONDARY,
            self.password_show_entry_pixbuf
        )
        self.proton_password_entry.set_icon_activatable(
            Gtk.EntryIconPosition.SECONDARY,
            True
        )
        self.proton_password_entry.connect(
            "icon-press", self.on_change_password_visibility
        )

    def setup_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_path(os.path.join(CSS_DIR_PATH, "login.css"))
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def setup_actions(self):
        # create action
        need_help_action = Gio.SimpleAction.new("need_help", None)
        login_action = Gio.SimpleAction.new("login", None)

        # connect action to callback
        need_help_action.connect("activate", self.on_display_popover)
        login_action.connect(
            "activate", self.thread_on_clicked_login, self.on_clicked_login
        )

        # add action
        self.add_action(need_help_action)
        self.add_action(login_action)

    def on_change_password_visibility(
        self, gtk_entry_object, gtk_icon_object, gtk_event
    ):
        is_text_visible = gtk_entry_object.get_visibility()
        gtk_entry_object.set_visibility(not is_text_visible)
        pixbuf = (
            self.password_show_entry_pixbuf
            if is_text_visible
            else self.password_hide_entry_pixbuf)
        self.proton_password_entry.set_icon_from_pixbuf(
            Gtk.EntryIconPosition.SECONDARY,
            pixbuf
        )

    def on_display_popover(self, gio_simple_action, _):
        self.popover_login_menu.show()

    def thread_on_clicked_login(self, *args, **kwargs):
        args_list = list(args)
        callback_method = args_list.pop(2)
        args = tuple(args_list)

        if not self.login_button.get_property("sensitive"):
            return

        thread = threading.Thread(target=callback_method, args=(args, kwargs))
        thread.daemon = True
        thread.start()

    def on_clicked_login(self, gio_simple_action, _):
        self.overlay_spinner.start()
        if self.top_banner_revealer_grid_context.has_class("banner-error"):
            self.top_banner_revealer_grid_context.remove_class("banner-error")
        self.top_banner_revealer.set_reveal_child(False)
        self.overlay_box.set_property("visible", True)
        self.login_presenter.login()

    def update_login_status(self, result):
        if result is not None:
            self.overlay_spinner.stop()
            self.banner_error_label.set_text(result)
            self.top_banner_revealer_grid_context.add_class("banner-error")
            self.top_banner_revealer.set_reveal_child(True)
            self.overlay_box.set_property("visible", False)
        else:
            self.dashboard_window().present()
            self.close()

    def set_css_class(self, gtk_object, add_css_class, remove_css_class=None):
        gtk_object_context = gtk_object.get_style_context()
        if (
            gtk_object_context.has_class(add_css_class)
            or (
                gtk_object_context.has_class(add_css_class)
                and remove_css_class
                and not add_css_class == remove_css_class
                and not gtk_object_context.has_class(remove_css_class)
            )
        ):
            return

        if remove_css_class and gtk_object_context.has_class(remove_css_class):
            gtk_object_context.remove_class(remove_css_class)

        gtk_object_context.add_class(add_css_class)
