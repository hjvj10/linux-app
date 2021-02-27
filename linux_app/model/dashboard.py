import requests
from ..logger import logger


class DashboardModel:

    def __init__(self, protonvpn):
        self.protonvpn = protonvpn

    def get_ip(self):
        logger.info("Getting IP")
        try:
            r = requests.get("https://ip.me/")
            ip = r.text.strip()
        except (Exception, requests.exceptions.BaseHTTPError) as e:
            logger.exception(e)
            ip = "Unable to fetch IP"

        logger.info("IP fetched")

        return ip
