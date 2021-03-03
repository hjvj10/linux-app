from typing import Callable

from ... import operators as ops
from ...core import Observable, pipe
from ...core.typing import Predicate


def _all(predicate: Predicate) -> Callable[[Observable], Observable]:

    filtering = ops.filter(lambda v: not predicate(v))
    mapping = ops.map(lambda b: not b)
    some = ops.some()

    return pipe(
        filtering,
        some,
        mapping
    )
