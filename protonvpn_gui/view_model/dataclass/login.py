from dataclasses import dataclass
from enum import Enum, auto


class LoginState(Enum):
    IN_PROGRESS = auto()
    SUCCESS = auto()


@dataclass
class LoginError:
    message: str
    display_troubleshoot_dialog: bool = False