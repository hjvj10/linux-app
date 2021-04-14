from dataclasses import dataclass
from enum import Enum, auto
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib import exceptions
from ..rx.subject.replaysubject import ReplaySubject
from ..logger import logger
from protonvpn_nm_lib.enums import KillswitchStatusEnum


class LoginState(Enum):
    IN_PROGRESS = auto()
    SUCCESS = auto()


@dataclass
class LoginError:
    message: str


class LoginViewModel:

    def __init__(self, bg_process):
        self.bg_process = bg_process
        self.user_settings = protonvpn.get_settings()
        self.state = ReplaySubject(buffer_size=1)

    def login(self, username, password):
        self.state.on_next(LoginState.IN_PROGRESS)
        process = self.bg_process.setup(
            self.login_sync, username, password
        )
        process.start()

    def login_sync(self, username, password):
        result = None
        try:
            protonvpn.login(username, password)
            result = LoginState.SUCCESS
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            result = LoginError("{}".format(str(e)))

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
