import threading
from dataclasses import dataclass
from enum import Enum, auto

from protonvpn_nm_lib import exceptions
from ..rx.subject.replaysubject import ReplaySubject


class LoginState(Enum):
    IN_PROGRESS = auto()
    SUCCESS = auto()


@dataclass
class LoginError:
    message: str


class LoginViewModel:

    def __init__(self, protonvpn):
        self.protonvpn = protonvpn

        self.state = ReplaySubject(buffer_size=1)

    def login(self, username, password):
        self.state.on_next(LoginState.IN_PROGRESS)

        # consider some alternative to threading.Thread for concurrency,
        #    like asyncio or from rx library.
        threading.Thread(
            target=self.login_sync, args=(username, password)
        ).start()

    def login_sync(self, username, password):
        result = None
        try:
            self.protonvpn._login(username, password)
            result = LoginState.SUCCESS
        except (exceptions.ProtonVPNException, Exception) as e:
            result = LoginError("{}".format(str(e)))

        self.state.on_next(result)
