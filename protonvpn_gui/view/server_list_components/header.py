from ...factory import WidgetFactory


class Header:
    def __init__(self, app):
        self.app = app
        self.__grid = WidgetFactory.grid("default")
        self.__grid.add_class("server-list-country-margin-left")
        self.__grid.add_class("server-list-country-margin-right")
        self.__grid.add_class("country-header")
        self.__grid.add_class("header-background-color")
        self.__header_title = WidgetFactory.label("default")
        self.__header_title.add_class("dark-text-color")
        self.__button = WidgetFactory.button("header_info")
        self.__button.show = False
        self.__info_icon = WidgetFactory.image("server_feature_info")
        self.__info_icon_hovered = WidgetFactory.image("server_feature_info_hover")
        self.__button.custom_content(self.__info_icon.widget)
        self.__attach_widgets()
        self.__add_icon_hover()

    @property
    def widget(self):
        return self.__grid.widget

    def __attach_widgets(self):
        self.__grid.attach(self.__header_title.widget)
        self.__grid.attach_right_next_to(self.__button.widget, self.__header_title.widget)

    def __add_icon_hover(self):
        self.__button.connect("enter-notify-event", self.__add_hover)
        self.__button.connect("leave-notify-event", self.__remove_hover)

    def __add_hover(self, *_):
        self.__button.widget.remove(self.__info_icon.widget)
        self.__button.custom_content(self.__info_icon_hovered.widget)

    def __remove_hover(self, *_):
        self.__button.widget.remove(self.__info_icon_hovered.widget)
        self.__button.custom_content(self.__info_icon.widget)

    @property
    def show(self):
        return self.__grid.show

    @show.setter
    def show(self, newboolval):
        self.__grid.show = newboolval

    @property
    def info_icon_visibility(self):
        return self.__button.show

    @info_icon_visibility.setter
    def info_icon_visibility(self, newboolval):
        self.__button.show = newboolval

    @property
    def title(self):
        return self.__header_title.content

    @title.setter
    def title(self, newvalue):
        self.__header_title.content = newvalue

    def connect_button(self, func, *args):
        self.__button.connect("clicked", func, *args)
