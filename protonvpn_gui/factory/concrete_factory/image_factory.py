import os

import gi

from ...constants import (ICON_DIR_PATH, IMG_DIR_PATH, KILLSWITCH_ICON_SET,
                          NETSHIELD_ICON_SET, SECURE_CORE_ICON_SET)
from ...enums import (DashboardKillSwitchIconEnum, DashboardNetshieldIconEnum,
                      DashboardSecureCoreIconEnum)

gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf, Gtk

from ..abstract_widget_factory import WidgetFactory


class ImageFactory(WidgetFactory):
    concrete_factory = "image"

    def __init__(self):
        self.__widget = Gtk.Image()
        self.__widget_context = self.__widget.get_style_context()

    @classmethod
    def factory(cls, widget_name, extra_arg=None):
        subclasses_dict = cls._get_subclasses_dict("image")
        return subclasses_dict[widget_name](extra_arg)

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
    def tooltip_text(self):
        return self.__widget.get_tooltip_text()

    @tooltip_text.setter
    def tooltip_text(self, newvalue):
        self.__widget.set_tooltip_text(newvalue)

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

    def replace_with_new_img(self, img_path, width, height):
        pixbuff = self.create_image_pixbuf_from_name(
            img_path,
            width=height, height=width
        )
        self.set_from_pixbuf(pixbuff)

    def replace_with_new_icon(self, img_path, width, height):
        pixbuff = self.create_icon_pixbuf_from_name(
            img_path,
            width=width, height=height
        )
        self.set_from_pixbuf(pixbuff)

    def set_from_pixbuf(self, pixbuf_widget):
        self.__widget.set_from_pixbuf(pixbuf_widget)

    def create_icon_pixbuf_from_name(
        self, icon_name, width=None, height=None
    ):
        """Gets the icon pixbuff for the specified filename.

        If width and/or height are not provided, then the icon
        is set with original values. Else, the icon is resized.

        Args:
            icon_name (string):
            width (int|float): optional
            height (int|float): optional

        Returns:
            GdkPixbuf instance with loaded image
        """
        if width and height:
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=os.path.join(
                    ICON_DIR_PATH,
                    icon_name,

                ),
                width=width,
                height=height,
                preserve_aspect_ratio=True
            )

        return GdkPixbuf.Pixbuf.new_from_file(
            filename=os.path.join(
                ICON_DIR_PATH,
                icon_name
            )
        )

    def create_image_pixbuf_from_name(
        self, image_name, width=None, height=None
    ):
        """Gets the icon pixbuff for the specified filename.

        If width and/or height are not provided, then the image
        is set with original values. Else, the image is resized.

        Args:
            icon_name (string):
            width (int|float): optional
            height (int|float): optional

        Returns:
            GdkPixbuf instance with loaded image
        """
        if width and height:
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=os.path.join(
                    IMG_DIR_PATH,
                    image_name
                ),
                width=width,
                height=height,
                preserve_aspect_ratio=True
            )

        return GdkPixbuf.Pixbuf.new_from_file(
            filename=os.path.join(
                IMG_DIR_PATH,
                image_name
            )
        )


class Dummy(ImageFactory):
    """Dummy class."""
    image = "dummy"

    def __init__(self, _):
        super().__init__()


class Chevron(ImageFactory):
    """Chevron icon class."""
    image = "chevron_icon"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                "chevron-default.svg",
                width=25, height=25
            )
        )
        self.show = True


class Maintenance(ImageFactory):
    """Maintenance icon class."""
    image = "maintenance_icon"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                "maintenance-icon.svg",
                width=20, height=20
            )
        )
        self.add_class("server-icon")
        self.show = False


class FeatureP2P(ImageFactory):
    """FeatureP2P icon class."""
    image = "p2p_icon"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                "p2p-arrows.png",
                width=20, height=20
            )
        )
        self.add_class("server-icon")
        self.show = True


class FeatureTOR(ImageFactory):
    """FeatureTOR icon class."""
    image = "tor_icon"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                "tor-onion.png",
                width=20, height=20
            )
        )
        self.add_class("server-icon")
        self.show = True


class FeaturePlus(ImageFactory):
    """FeaturePlus icon class."""
    image = "plus_icon"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                "plus-server.png",
                width=20, height=20
            )
        )
        self.add_class("server-icon")
        self.show = True


class LargeFlag(ImageFactory):
    """LargeFlag class."""
    image = "large_flag"

    def __init__(self, country_code):
        super().__init__()
        self.align_v = Gtk.Align.CENTER
        self.add_class("country-flag")
        self.set_from_pixbuf(
            self.create_image_pixbuf_from_name(
                "flags/large/" + country_code.lower() + ".jpg",
                width=400, height=400
            )
        )
        self.show = True


class SmallFlag(ImageFactory):
    """SmallFlag class."""
    image = "small_flag"

    def __init__(self, country_code):
        super().__init__()
        self.align_v = Gtk.Align.CENTER
        self.add_class("country-flag")
        self.set_from_pixbuf(
            self.create_image_pixbuf_from_name(
                "flags/small/" + country_code.lower() + ".png",
                width=15, height=15
            )
        )
        self.show = True


class DummySmallFlag(ImageFactory):
    """DummySmallFlag class."""
    image = "dummy_small_flag"

    def __init__(self, _):
        super().__init__()
        self.align_v = Gtk.Align.CENTER
        self.add_class("country-flag")
        self.show = True


class Load(ImageFactory):
    """Load icon class."""
    image = "load_icon_flag"

    def __init__(self, tooltip_text):
        super().__init__()
        self.tooltip = True
        self.tooltip_text = tooltip_text
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                "info-icon.svg",
                width=10, height=10
            )
        )
        self.add_class("server-icon")
        self.show = True


class SecureCoreChevron(ImageFactory):
    """SecureCoreOff icon class."""
    image = "secure_core_chevron"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                SECURE_CORE_ICON_SET[DashboardSecureCoreIconEnum.CHEVRON],
                width=11, height=11
            )
        )
        self.add_class("country-flag")
        self.show = True


class SecureCoreOff(ImageFactory):
    """SecureCoreOff icon class."""
    image = "secure_core_off"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                SECURE_CORE_ICON_SET[DashboardSecureCoreIconEnum.OFF],
                width=25, height=25
            )
        )
        self.show = True


class SecureCoreOn(ImageFactory):
    """SecureCoreOn icon class."""
    image = "secure_core_on"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                SECURE_CORE_ICON_SET[DashboardSecureCoreIconEnum.ON_DEFAULT],
                width=25, height=25
            )
        )
        self.show = True


class NetshiledOff(ImageFactory):
    """NetshieldOff icon class."""
    image = "netshield_off"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                NETSHIELD_ICON_SET[DashboardNetshieldIconEnum.OFF],
                width=25, height=25
            )
        )
        self.show = True


class NetshiledMalware(ImageFactory):
    """NetshieldMalware icon class."""
    image = "netshield_malware"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                NETSHIELD_ICON_SET[DashboardNetshieldIconEnum.MALWARE_DEFAULT],
                width=25, height=25
            )
        )
        self.show = True


class NetshiledAdsMalware(ImageFactory):
    """NetshiledAdsMalware icon class."""
    image = "netshield_ads_malware"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                NETSHIELD_ICON_SET[DashboardNetshieldIconEnum.MALWARE_ADS_DEFAULT], # noqa
                width=25, height=25
            )
        )
        self.show = True


class KillSwitchOff(ImageFactory):
    """KillSwitchOff icon class."""
    image = "killswitch_off"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                KILLSWITCH_ICON_SET[DashboardKillSwitchIconEnum.OFF],
                width=25, height=25
            )
        )
        self.show = True


class KillSwitchOn(ImageFactory):
    """KillSwitchOn icon class."""
    image = "killswitch_on"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                KILLSWITCH_ICON_SET[DashboardKillSwitchIconEnum.ON_DEFAULT],
                width=25, height=25
            )
        )
        self.show = True


class KillSwitchAlwaysOn(ImageFactory):
    """KillSwitchAlwaysOn icon class."""
    image = "killswitch_always_on"

    def __init__(self, _):
        super().__init__()
        self.set_from_pixbuf(
            self.create_icon_pixbuf_from_name(
                KILLSWITCH_ICON_SET[DashboardKillSwitchIconEnum.ALWAYS_ON_DEFAULT], # noqa
                width=25, height=25
            )
        )
        self.show = True
