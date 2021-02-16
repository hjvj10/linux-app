import threading
from dataclasses import dataclass
from enum import Enum, auto

from protonvpn_nm_lib import exceptions
from protonvpn_nm_lib.services.user_manager import UserManager
from rx.subject.replaysubject import ReplaySubject


class LoginState(Enum):
    IN_PROGRESS = auto()
    SUCCESS = auto()


@dataclass
class LoginError:
    message: str


class LoginPresenter:

    def __init__(
        self,
        reconector_manager,
        user_conf_manager,
        ks_manager,
        connection_manager,
        user_manager: UserManager,  # use type hints for external deps
        server_manager,
        ipv6_lp_manager
    ):
        self.reconector_manager = reconector_manager
        self.user_conf_manager = user_conf_manager
        self.ks_manager = ks_manager
        self.connection_manager = connection_manager
        self.user_manager = user_manager
        self.server_manager = server_manager
        self.ipv6_lp_manager = ipv6_lp_manager

        self.state = ReplaySubject(buffer_size=1)

    def login(self, username, password):
        self.state.on_next(LoginState.IN_PROGRESS)

        # consider some alternative to threading.Thread for concurrency,
        #    like asyncio or from rx library.
        threading.Thread(target=self.login_sync, args=(username, password)).start()

    def login_sync(self, username, password):
        result = None
        try:
            self.user_manager.login(username, password)
            result = LoginState.SUCCESS
        except (TypeError, ValueError) as e:
            result = LoginError("Unable to authenticate: {}.".format(e))  # use translated strings
        except (exceptions.API8002Error, exceptions.API85032Error) as e:
            result = LoginError("{}".format(e))
        except exceptions.APITimeoutError:
            result = LoginError("Connection timeout, unable to reach API.")
        except (exceptions.UnhandledAPIError, exceptions.APIError) as e:
            result = LoginError("Unhandled API error occured: {}".format(e))
        except exceptions.ProtonSessionWrapperError as e:
            result = LoginError("Unknown API error occured: {}.".format(e))
        except (exceptions.ProtonVPNException, Exception) as e:
            # logger.exception(
            #     "[!] Unknown error: {}".format(e)
            # )
            result = LoginError("Unknown error occured: {}.".format(e))

        self.state.on_next(result)
