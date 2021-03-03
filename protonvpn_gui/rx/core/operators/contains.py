from typing import Any, Callable, Optional

from ... import operators as ops
from ...core import Observable, pipe
from ...core.typing import Comparer
from ...internal.basic import default_comparer


def _contains(value: Any,
              comparer: Optional[Comparer] = None
              ) -> Callable[[Observable], Observable]:
    comparer_ = comparer or default_comparer

    filtering = ops.filter(lambda v: comparer_(v, value))
    something = ops.some()

    return pipe(filtering, something)
