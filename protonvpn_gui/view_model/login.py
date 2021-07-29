from dataclasses import dataclass
from enum import Enum, auto
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib import exceptions
from ..rx.subject.replaysubject import ReplaySubject
from ..logger import logger
from protonvpn_nm_lib.enums import KillswitchStatusEnum
from ..patterns.factory import BackgroundProcess


class LoginState(Enum):
    IN_PROGRESS = auto()
    SUCCESS = auto()


@dataclass
class LoginError:
    message: str
    display_troubleshoot_dialog: bool = True


class LoginViewModel:

    def __init__(self):
        self.user_settings = protonvpn.get_settings()
        self.state = ReplaySubject(buffer_size=1)
        self.__username = None
        self.__password = None

    def login_async(self, username, password):
        self.__username = username
        self.__password = password

        self.state.on_next(LoginState.IN_PROGRESS)
        process = BackgroundProcess.factory("gtask")
        process.setup(self.__login)
        process.start()

    def __login(self, *_):
        result = None
        try:
            protonvpn.login(self.__username, self.__password)
            result = LoginState.SUCCESS
        except exceptions.InsecureConnection as e:
            logger.exception(e)
            result = LoginError(
                "Your connection is not secure. "
                "Please change network and attempt a new connection.",
            )
        except exceptions.APITimeoutError as e:
            logger.exception(e)
            result = LoginError(
                "Connection to API timed out.",
            )
        except exceptions.APIError as e:
            logger.exception(e)
            result = LoginError(
                "Error in reaching API.",
            )
        except exceptions.UnknownAPIError as e:
            logger.exception(e)
            result = LoginError(
                "Unknown API error.",
            )
        except (
            exceptions.API8002Error, exceptions.API5002Error,
            exceptions.API5003Error
        ) as e:
            logger.exception(e)
            result = LoginError(
                str(e),
                False
            )
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = LoginError(
                "Unknown error occured. If the issue persists, please contact support.",
                False
            )

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
