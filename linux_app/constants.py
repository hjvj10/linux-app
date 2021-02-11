import os

APP_VERSION = "0.0.2"

ABSOLUTE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR_PATH = os.path.join(ABSOLUTE_DIR_PATH, "assets")

UI_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "ui")
CSS_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "css")
ICON_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "icons")
IMG_DIR_PATH = os.path.join(ASSETS_DIR_PATH, "img")
