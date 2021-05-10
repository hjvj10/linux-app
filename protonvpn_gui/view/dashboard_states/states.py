from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.constants import SUPPORTED_PROTOCOLS
from protonvpn_nm_lib.enums import ProtocolImplementationEnum
from ...enums import GLibEventSourceEnum


class InitLoadView:
    """UI class.

    Setup the UI to an initial loading state (app start).
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.overlay_bottom_label.props.label = ""\
            "Secure Internet Anywhere"
        dv.overlay_spinner.start()
        dv.overlay_box.props.visible = True


class UpdateNetworkSpeedView:
    """UI class.

    Updates network speeds labels.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.upload_speed_label.props.label = state.upload
        dv.download_speed_label.props.label = state.download


class NotConnectedVPNView:
    """UI class.

    Setup the UI to not connected state.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        label = "You are not connected"
        ip = state.ip

        if state.ks_enabled:
            label = "Kill Switch activated!"
            ip = ""
            dv.application.indicator.set_error_state()
        elif all(
            attr is None
            for attr
            in [state.ip, state.isp, state.country]
        ):
            label = "Network issues detected."
            ip = ""
            dv.application.indicator.set_error_state()
        else:
            dv.application.indicator.set_disconnected_state()

        dv.connected_protocol_label.props.label = ""
        dv.country_servername_label.props.label = \
            label
        dv.ip_label.props.label = ip
        label_ctx = dv.country_servername_label.get_style_context()
        dv.quick_connect_button.props.visible = True
        dv.main_disconnect_button.props.visible = False
        if not label_ctx.has_class("warning-color"):
            label_ctx.add_class("warning-color")


        dv.add_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        dv.add_background_glib(GLibEventSourceEnum.ON_SERVER_LOAD)
        dv.gtk_property_setter(
            dv.SET_UI_NOT_CONNECTED
        )


class ConnectedVPNView:
    """UI class.

    Setup the UI to connected state.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        country = protonvpn.get_country()
        country_string = "{}".format(
            country.get_country_name(state.countries[0])
        )
        if len(state.countries) > 1:
            country_string = "{}".format(country.get_country_name(
                state.countries[0]
            ))
            country_string = country_string + " >> {}".format(
                country.get_country_name(state.countries[1])
            )
        else:
            country_string = country_string + " {}".format(state.servername)

        dv.on_connect_load_sidebar_flag(state.exit_country_code)
        country_servername = country_string
        dv.country_servername_label.props.label = country_servername
        dv.ip_label.props.label = state.ip
        dv.serverload_label.props.label = state.load + "% " + "Load"
        protocol = state.protocol
        if state.protocol in SUPPORTED_PROTOCOLS[
            ProtocolImplementationEnum.OPENVPN
        ]:
            protocol = "OpenVPN ({})".format(
                state.protocol.value.upper()
            )
        dv.connected_protocol_label.props.label = protocol
        dv.quick_connect_button.props.visible = False
        dv.main_disconnect_button.props.visible = True
        label_ctx = dv.country_servername_label.get_style_context()

        if label_ctx.has_class("warning-color"):
            label_ctx.remove_class("warning-color")

        dv.application.indicator.set_connected_state()

        dv.add_background_glib(GLibEventSourceEnum.ON_MONITOR_NETWORK_SPEED)
        dv.add_background_glib(GLibEventSourceEnum.ON_MONITOR_VPN)
        dv.add_background_glib(GLibEventSourceEnum.ON_SERVER_LOAD)
        dv.gtk_property_setter(dv.SET_UI_CONNECTED)


class ConnectVPNPreparingView:
    """UI class.

    Setup the UI during VPN prepare state.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        dv.connecting_overlay_spinner.props.visible = True
        dv.connecting_progress_bar.props.visible = True
        dv.connecting_progress_bar.set_fraction(0.2)
        dv.connecting_to_label.props.label = "Preparing ProtonVPN Connection"
        dv.cancel_connect_overlay_button.props.visible = False
        dv.connecting_overlay_box.props.visible = True


class ConnectVPNInProgressView:
    """UI class.

    Setup the UI during VPN connection in progress state.
    """
    def __init__(self, dashboard_view, state):
        dv = dashboard_view
        new_value = dv.connecting_progress_bar.get_fraction() + 0.5
        dv.connecting_progress_bar.set_fraction(new_value)
        var_1 = state.exit_country
        var_2 = state.servername
        if state.is_secure_core:
            var_1 = state.entry_country
            var_2 = state.exit_country

        dv.connecting_to_label.set_markup(
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
        dv = dashboard_view
        dv.connecting_to_label.set_text(
            state.message
        )
        dv.connecting_to_label.props.visible = False
        dv.cancel_connect_overlay_button.props.visible = True
        dv.cancel_connect_overlay_button.set_label("Close")
        dv.connecting_overlay_spinner.props.visible = False
        dv.connecting_progress_bar.props.visible = False
