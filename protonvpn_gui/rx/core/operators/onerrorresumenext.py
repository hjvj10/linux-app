from typing import Callable

from ... import on_error_resume_next as rx_on_error_resume_next
from ...core import Observable


def _on_error_resume_next(second: Observable) -> Callable[[Observable], Observable]:
    def on_error_resume_next(source: Observable) -> Observable:
        return rx_on_error_resume_next(source, second)
    return on_error_resume_next
