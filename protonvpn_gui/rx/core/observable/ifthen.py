from typing import Callable, Union, cast
from asyncio import Future

from ... import empty, from_future, defer
from ...core import Observable
from ...core.typing import Scheduler
from ...internal.utils import is_future


def _if_then(condition: Callable[[], bool],
             then_source: Union[Observable, Future],
             else_source: Union[None, Observable, Future] = None
             ) -> Observable:
    """Determines whether an observable collection contains values.

    Example:
    1 - res = if_then(condition, obs1)
    2 - res = if_then(condition, obs1, obs2)

    Args:
        condition: The condition which determines if the then_source or
            else_source will be run.
        then_source: The observable sequence or Promise that
            will be run if the condition function returns true.
        else_source: [Optional] The observable sequence or
            Promise that will be run if the condition function returns
            False. If this is not provided, it defaults to
            empty

    Returns:
        An observable sequence which is either the then_source or
        else_source.
    """

    else_source = else_source or empty()

    then_source = from_future(cast(Future, then_source)) if is_future(then_source) else then_source
    else_source = from_future(cast(Future, else_source)) if is_future(else_source) else else_source

    def factory(_: Scheduler):
        return then_source if condition() else else_source

    return defer(factory)
