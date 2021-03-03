from asyncio import Future
from typing import cast, Callable, Union
import itertools

from ... import from_future as rx_from_future, concat_with_iterable as rx_concat_with_iterable
from ...core import Observable
from ...core.typing import Predicate
from ...internal.utils import is_future, infinite


def _while_do(condition: Predicate) -> Callable[[Observable], Observable]:
    def while_do(source: Union[Observable, Future]) -> Observable:
        """Repeats source as long as condition holds emulating a while
        loop.

        Args:
            source: The observable sequence that will be run if the
                condition function returns true.

        Returns:
            An observable sequence which is repeated as long as the
            condition holds.
        """
        if is_future(source):
            obs = rx_from_future(cast(Future, source))
        else:
            obs = cast(Observable, source)
        it = itertools.takewhile(condition, (obs for _ in infinite()))
        return rx_concat_with_iterable(it)
    return while_do
