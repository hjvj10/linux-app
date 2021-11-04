from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.constants import SUPPORTED_PROTOCOLS
from protonvpn_nm_lib.enums import ProtocolImplementationEnum
from ...enums import GLibEventSourceEnum, DashboardFeaturesEnum
from ...patterns.factory import WidgetFactory
from ...view_model.dataclass.dashboard import GenericEvent


class InitLoadView:
    """UI class.

    Setup the UI to an initial loading state (app start).
    """
    def __init__(self, dashboard_view, state):
        dashboard_view.overlay_bottom_label.props.label = ""\
            "Secure Internet Anywhere"
        dashboard_view.overlay_spinner.start()
        dashboard_view.overlay_box.props.visible = True


class UpdateNetworkSpeedView:
    """UI class.

    Updates network speeds labels.
    """
    def __init__(self, dashboard_view, state):
        dashboard_view.upload_speed_label.props.label = state.upload
        dashboard_view.download_speed_label.props.label = state.download


class NotConnectedVPNView:
    """UI class.

    Setup the UI to not connected state.
    """
    def __init__(self, dashboard_view, state):
        label = "You are not connected"
        ip = state.ip

        if state.perma_ks_enabled:
            label = "Kill Switch activated!"
            ip = ""
            dashboard_view.application.indicator.set_error_state()
        elif all(
            attr is None
            for attr
            in [state.ip, state.isp, state.country]
        ):
            label = "Network issues detected."
            ip = ""
            dashboard_view.application.indicator.set_error_state()
        else:
            dashboard_view.application.indicator.set_disconnected_state()

        dashboard_view.quick_connect_button.props.sensitive = True

        dashboard_view.connected_protocol_label.props.label = ""
        dashboard_view.country_servername_label.props.label = \
            label
        dashboard_view.ip_label.props.label = ip
        label_ctx = dashboard_view.country_servername_label.get_style_context()
        dashboard_view.quick_connect_button.props.visible = True
        dashboard_view.main_disconnect_button.props.visible = False

        if not label_ctx.has_class("warning-color"):
            label_ctx.add_class("warning-color")

        dashboard_view.add_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        dashboard_view.add_background_glib(GLibEventSourceEnum.ON_SERVER_LOAD)
        dashboard_view.gtk_property_setter(dashboard_view.SET_UI_NOT_CONNECTED)
        if not dashboard_view.glib_source_tracker[GLibEventSourceEnum.ON_EVENT]:
            dashboard_view.add_background_glib(GLibEventSourceEnum.ON_EVENT)


class ConnectedVPNView:
    """UI class.

    Setup the UI to connected state.
    """
    def __init__(self, dashboard_view, state):
        country = protonvpn.get_country()
        country_string = "{}".format(
            country.get_country_name(state.countries[0])
        )
        if len(state.countries) > 1:
            country_string = "{}".format(country.get_country_name(
                state.countries[0]
            ))
            country_string = "{} >> {}".format(
                country.get_country_name(state.countries[1]),
                country_string
            )
        else:
            country_string = country_string + " {}".format(state.servername)

        dashboard_view.on_connect_load_sidebar_flag(state.exit_country_code)
        country_servername = country_string
        dashboard_view.country_servername_label.props.label = country_servername
        dashboard_view.ip_label.props.label = state.ip
        dashboard_view.serverload_label.props.label = state.load + "% " + "Load"
        protocol = state.protocol
        if state.protocol in SUPPORTED_PROTOCOLS[
            ProtocolImplementationEnum.OPENVPN
        ]:
            protocol = "OpenVPN ({})".format(
                state.protocol.value.upper()
            )
        dashboard_view.connected_protocol_label.props.label = protocol
        dashboard_view.quick_connect_button.props.visible = False
        dashboard_view.main_disconnect_button.props.visible = True
        dashboard_view.main_disconnect_button.props.sensitive = True
        label_ctx = dashboard_view.country_servername_label.get_style_context()

        if label_ctx.has_class("warning-color"):
            label_ctx.remove_class("warning-color")

        dashboard_view.application.indicator.set_connected_state()

        dashboard_view.add_background_glib(GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED)
        dashboard_view.add_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        dashboard_view.add_background_glib(GLibEventSourceEnum.ON_SERVER_LOAD)
        dashboard_view.gtk_property_setter(dashboard_view.SET_UI_CONNECTED)
        if not dashboard_view.glib_source_tracker[GLibEventSourceEnum.ON_EVENT]:
            dashboard_view.add_background_glib(GLibEventSourceEnum.ON_EVENT)


class ConnectVPNPreparingView:
    """UI class.

    Setup the UI during VPN prepare state.
    """
    def __init__(self, dashboard_view, state):
        dashboard_view.connecting_overlay_spinner.props.visible = True
        dashboard_view.connecting_progress_bar.props.visible = True
        dashboard_view.connecting_progress_bar.set_fraction(0.2)
        dashboard_view.connecting_to_label.props.label = "Preparing ProtonVPN Connection"
        dashboard_view.cancel_connect_overlay_button.props.visible = False
        dashboard_view.connecting_overlay_box.props.visible = True


class ConnectVPNInProgressView:
    """UI class.

    Setup the UI during VPN connection in progress state.
    """
    def __init__(self, dashboard_view, state):
        new_value = dashboard_view.connecting_progress_bar.get_fraction() + 0.5
        dashboard_view.connecting_progress_bar.set_fraction(new_value)
        var_1 = state.exit_country
        var_2 = state.servername
        if state.is_secure_core:
            var_1 = state.entry_country
            var_2 = state.exit_country

        dashboard_view.connecting_to_label.set_markup(
            "Connecting <span weight='bold'>{} >> {}</span>".format(
                var_1, var_2,
            )
        )


class ConnectVPNErrorView:
    """UI class.

    Setup the UI state when an error occurs
    during attempt to connect.
    """
    def __init__(self, dashboard_view, state):
        dashboard_view.connecting_to_label.set_text(
            state.message
        )
        dashboard_view.quick_connect_button.props.sensitive = True
        dashboard_view.main_disconnect_button.props.sensitive = False
        dashboard_view.connecting_to_label.props.visible = False
        dashboard_view.cancel_connect_overlay_button.props.visible = True
        dashboard_view.cancel_connect_overlay_button.set_label("Close")
        dashboard_view.connecting_overlay_spinner.props.visible = False
        dashboard_view.connecting_progress_bar.props.visible = False


class UpdateQuickSettings:
    """UI class.

    Update quick settings.
    """
    def __init__(self, dashboard_view, state):
        self.update_quick_settings(dashboard_view, state)

    def update_quick_settings(self, dashboard_view, state):
        """Updates quick settings icons based on state.

        Args:
            state (QuickSettingsStatus)

        QuickSettingsStatus of three different properties:
            secure_core (DashboardSecureCoreIconEnum)
            netshield (DashboardNetshieldIconEnum)
            killswitch (DashboardKillSwitchIconEnum)
        """
        _dummy_object = WidgetFactory.image("dummy")
        dummy_object = weakref.proxy(_dummy_object)

        feature_button_secure_core_pixbuf = dummy_object \
            .create_icon_pixbuf_from_name(
                dashboard_view.features_icon_set_dict[
                    DashboardFeaturesEnum.SECURE_CORE
                ][state.secure_core],
                width=dashboard_view.feature_button_icon_width,
                height=dashboard_view.feature_button_icon_height
            )
        feature_button_netshield_pixbuf = dummy_object \
            .create_icon_pixbuf_from_name(
                dashboard_view.features_icon_set_dict[
                    DashboardFeaturesEnum.NETSHIELD
                ][state.netshield],
                width=dashboard_view.feature_button_icon_width,
                height=dashboard_view.feature_button_icon_height
            )
        feature_button_killswitch_pixbuf = dummy_object \
            .create_icon_pixbuf_from_name(
                dashboard_view.features_icon_set_dict[
                    DashboardFeaturesEnum.KILLSWITCH
                ][state.killswitch],
                width=dashboard_view.feature_button_icon_width,
                height=dashboard_view.feature_button_icon_height
            )

        dashboard_view.dashboard_secure_core_button_image.set_from_pixbuf(
            feature_button_secure_core_pixbuf
        )
        dashboard_view.dashboard_netshield_button_image.set_from_pixbuf(
            feature_button_netshield_pixbuf
        )
        dashboard_view.dashboard_killswitch_button_image.set_from_pixbuf(
            feature_button_killswitch_pixbuf
        )


class EventNotification:
    def __init__(self, dashboard_view, state):
        self.load_events(dashboard_view, state)

    def load_events(self, dashboard_view, state):
        if isinstance(state.event_dataclass, GenericEvent):
            self.__check_if_generic_event_should_be_displayed(
                dashboard_view, state.event_dataclass.class_instance,
                state.has_notification_been_opened, state.set_notification_as_read
            )

    def __check_if_generic_event_should_be_displayed(self, *args):
        dashboard_view, event_data, has_notification_been_opened, set_as_read = args

        icon_path = list(filter(lambda x: "ic-gift.png" in x, event_data.icon_paths))

        if not event_data.can_be_displayed or not bool(len(icon_path)):
            child = dashboard_view.connected_label_grid.get_child_at(1, 0)
            if dashboard_view.event_notification or child:
                try:
                    child.destroy()
                except AttributeError:
                    pass
                dashboard_view.event_notification = None

            return

        # Create "gift" widgets
        main_button = WidgetFactory.button("dashboard_event_button")
        event_icon = WidgetFactory.image("dashboard_event_icon", icon_path.pop())
        event_icon.tooltip_text = event_data.pill
        main_button.custom_content(event_icon.widget)

        # check if user has already opened event, if not display red dot
        if not has_notification_been_opened:
            event_icon.add_event_notitication()

        dashboard_view.connected_label_grid.attach(
            main_button.widget, 1, 0, 1, 1
        )
        dashboard_view.event_notification = main_button
        main_button.connect(
            "clicked", self.__open_modal,
            dashboard_view.application, event_data,
            set_as_read, event_icon
        )

    def __open_modal(self, gtk_button, *args):
        from ..dialog import GenericEventDialog
        application, event_data, set_as_read, event_icon = args

        event_icon.add_event_notitication(False)
        set_as_read()

        GenericEventDialog(application, event_data)
