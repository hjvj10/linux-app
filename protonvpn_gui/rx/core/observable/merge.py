# import rx

from ... import operators as ops
from ...core import Observable
from ... import from_iterable


def _merge(*sources: Observable) -> Observable:
    # return rx.from_iterable(sources).pipe(ops.merge_all())
    return from_iterable(sources).pipe(ops.merge_all())
