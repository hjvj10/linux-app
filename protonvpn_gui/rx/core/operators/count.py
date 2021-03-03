from typing import Callable, Optional
from ...core import Observable, pipe
from ...core.typing import Predicate

from ... import operators as ops


def _count(predicate: Optional[Predicate] = None) -> Callable[[Observable], Observable]:

    if predicate:
        filtering = ops.filter(predicate)
        return pipe(filtering, ops.count())

    counter = ops.reduce(lambda n, _: n + 1, seed=0)
    return pipe(counter)
