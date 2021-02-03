import os

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf, Gdk

from ...constants import CSS_DIR_PATH, UI_DIR_PATH, IMG_DIR_PATH, ICON_DIR_PATH

@Gtk.Template(filename=os.path.join(UI_DIR_PATH, "login.ui"))
class LoginWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'LoginWindow'

    proton_username_entry = Gtk.Template.Child()
    proton_password_entry = Gtk.Template.Child()
    login_button = Gtk.Template.Child()
    img_protonvpn_logo = Gtk.Template.Child()

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
            width=400,
            height=200,
            preserve_aspect_ratio=True
        )
        password_entry_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(
                ICON_DIR_PATH,
                "eye-show.imageset/eye-show@2x.png",

            ),
            width=15,
            height=15,
            preserve_aspect_ratio=True
        )

        self.img_protonvpn_logo.set_from_pixbuf(logo_pixbuf)
        self.proton_password_entry.set_icon_from_pixbuf(
            Gtk.EntryIconPosition.SECONDARY,
            password_entry_pixbuf
        )

    def setup_css(self):
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(os.path.join(CSS_DIR_PATH, "login.css"))
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


