from typing import Callable, Optional

from ... import operators as ops
from ...core import Observable, pipe
from ...core.typing import Mapper


def _sum(key_mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:
    if key_mapper:
        return pipe(
            ops.map(key_mapper),
            ops.sum()
        )

    return ops.reduce(seed=0, accumulator=lambda prev, curr: prev + curr)
