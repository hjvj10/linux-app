import os

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf, Gdk, Gio

from ...constants import CSS_DIR_PATH, UI_DIR_PATH, IMG_DIR_PATH, ICON_DIR_PATH

@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "login.ui"))
class LoginWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'LoginWindow'

    proton_username_entry = Gtk.Template.Child()
    proton_password_entry = Gtk.Template.Child()
    login_button = Gtk.Template.Child()
    img_protonvpn_logo = Gtk.Template.Child()
    icon_width = 18
    icon_heigt = 18
    password_show_entry_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=os.path.join(
            ICON_DIR_PATH,
            "eye-show.imageset/eye-show@3x.png",

        ),
        width=icon_width,
        height=icon_heigt,
        preserve_aspect_ratio=True
    )
    password_hide_entry_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=os.path.join(
            ICON_DIR_PATH,
            "eye-hide.imageset/eye-hide@3x.png",

        ),
        width=icon_width,
        height=icon_heigt,
        preserve_aspect_ratio=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_images()
        self.setup_css()

    def setup_images(self):
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
        self.proton_password_entry.set_icon_from_pixbuf(
            Gtk.EntryIconPosition.SECONDARY,
            self.password_show_entry_pixbuf
        )
        self.proton_password_entry.set_icon_activatable(
            Gtk.EntryIconPosition.SECONDARY,
            True
        )
        self.proton_password_entry.connect("icon-press", self.set_password_visibility)

    def setup_css(self):
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(os.path.join(CSS_DIR_PATH, "login.css"))
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def set_password_visibility(self, entry_object, icon_object, event):
        is_text_visible = entry_object.get_visibility()
        entry_object.set_visibility(not is_text_visible)
        pixbuf = (
            self.password_show_entry_pixbuf
            if is_text_visible
            else self.password_hide_entry_pixbuf)
        self.proton_password_entry.set_icon_from_pixbuf(
            Gtk.EntryIconPosition.SECONDARY,
            pixbuf
        )



