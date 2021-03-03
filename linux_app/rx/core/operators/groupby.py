from typing import Callable, Optional

from ... import never, operators as ops
from ...core import Observable
from ...core.typing import Mapper
from ...subject import Subject


def _group_by(key_mapper: Mapper,
              element_mapper: Optional[Mapper] = None,
              subject_mapper: Optional[Callable[[], Subject]] = None,
              ) -> Callable[[Observable], Observable]:

    def duration_mapper(_):
        return never()

    return ops.group_by_until(key_mapper, element_mapper, duration_mapper, subject_mapper)
