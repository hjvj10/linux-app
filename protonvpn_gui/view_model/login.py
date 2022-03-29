from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib import exceptions
from ..rx.subject.replaysubject import ReplaySubject
from ..logger import logger
from protonvpn_nm_lib.enums import KillswitchStatusEnum
from ..patterns.factory import BackgroundProcess
from .dataclass.login import LoginState, LoginError


class LoginViewModel:

    def __init__(self):
        self.user_settings = protonvpn.get_settings()
        self.__state = ReplaySubject(buffer_size=1)
        self.__username = None
        self.__password = None
        self.__captcha = None

    @property
    def state(self):
        from protonvpn_gui.rx.internal.exceptions import DisposedException
        try:
            self.__state.check_disposed()
        except DisposedException:
            self.__state = ReplaySubject(buffer_size=1)

        return self.__state

    @state.deleter
    def state(self):
        self.__state.dispose()

    def login_async(self, username=None, password=None, captcha=None):
        if username and password:
            self.__username = username
            self.__password = password

        self.__captcha = captcha

        self.state.on_next(LoginState.IN_PROGRESS)
        process = BackgroundProcess.factory("gtask")
        process.setup(self.__login)
        process.start()

    def __login(self, *_):
        result = None
        connection_error = False
        display_troubleshoot_dialog = False
        display_human_verification_dialog = False
        callback = None

        try:
            protonvpn.login(self.__username, self.__password, self.__captcha)
            result = LoginState.SUCCESS
        except exceptions.InsecureConnection as e:
            logger.exception(e)
            connection_error = "Your connection is not secure. " \
                "Please change network and attempt a new connection."
            display_troubleshoot_dialog = True
        except exceptions.APITimeoutError as e:
            logger.exception(e)
            connection_error = "Connection to API timed out."
            display_troubleshoot_dialog = True
        except exceptions.UnreacheableAPIError as e:
            logger.exception(e)
            connection_error = "Unable to reach API"
            display_troubleshoot_dialog = True
        except exceptions.APIError as e:
            logger.exception(e)
            connection_error = "Error in reaching API."
            display_troubleshoot_dialog = True
        except exceptions.NetworkConnectionError as e:
            logger.exception(e)
            connection_error = "Network Error"
            display_troubleshoot_dialog = True
        except exceptions.UnknownAPIError as e:
            logger.exception(e)
            connection_error = "Unknown API error."
        except (
            exceptions.API8002Error, exceptions.API5002Error,
            exceptions.API5003Error, exceptions.API85031Error,
            exceptions.API12087Error, exceptions.API2011Error
        ) as e:
            logger.exception(e)
            connection_error = str(e)
        except exceptions.API9001Error as e:
            logger.exception(e)
            connection_error = str(e)
            display_human_verification_dialog = protonvpn.get_session().captcha_url
            callback = self.login_async
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            connection_error = "Unknown error occurred. If the issue persists, " \
                "please contact support."

        if connection_error:
            result = LoginError(
                connection_error,
                display_troubleshoot_dialog,
                display_human_verification_dialog,
                callback
            )

        self.__captcha = None

        self.state.on_next(result)

    def is_killswitch_enabled(self):
        """Check if kill switch is enabled or not.

        Returns:
            bool
        """
        if self.user_settings.killswitch == KillswitchStatusEnum.HARD:
            return True

        return False

    def disable_killswitch(self):
        """Disable kill switch."""
        try:
            self.user_settings.killswitch = KillswitchStatusEnum.DISABLED
        except Exception as e:
            logger.exception(e)

    def can_url_be_reached(self, url):
        import requests

        try:
            requests.get(url, timeout=(3.0, 3.0))
        except: # noqa
            return False
        else:
            return True
