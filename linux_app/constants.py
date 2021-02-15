import os

from .enums import DashboardConnectionInfo

APP_VERSION = "0.0.2"
ABSOLUTE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR_PATH = os.path.join(ABSOLUTE_DIR_PATH, "assets")

UI_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "ui")
CSS_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "css")
ICON_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "icons")
IMG_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "img")

LOGGER_NAME = "protonvpn-gui"

DASHBOARD_CONNECTION_INFO = {
    DashboardConnectionInfo.COUNTRY_SERVERNAME_LABEL: None,
    DashboardConnectionInfo.IP_LABEL: None,
    DashboardConnectionInfo.SERVERLOAD_LABEL: None,
    DashboardConnectionInfo.SERVERLOAD_IMAGE: None,
    DashboardConnectionInfo.DOWNLOAD_SPEED_LABEL: None,
    DashboardConnectionInfo.DOWNLOAD_SPEED_IMAGE: None,
    DashboardConnectionInfo.UPLOAD_SPEED_LABEL: None,
    DashboardConnectionInfo.UPLOAD_SPEED_IMAGE: None
}
