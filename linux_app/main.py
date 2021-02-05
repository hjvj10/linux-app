import sys
import gi
import os

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio

from .view.login import LoginView

class ProtonVPN(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id='com.protonvpn.www',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        win = self.props.active_window

        if not win:
            win = LoginView(application=self)
        win.present()

def main():
    app = ProtonVPN()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

