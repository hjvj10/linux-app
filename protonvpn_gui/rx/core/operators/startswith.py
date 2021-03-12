from typing import Any, Callable

from ... import from_iterable, concat

from ...core import Observable


def _start_with(*args: Any) -> Callable[[Observable], Observable]:
    def start_with(source: Observable) -> Observable:
        """Partially applied start_with operator.

        Prepends a sequence of values to an observable sequence.

        Example:
            >>> start_with(source)

        Returns:
            The source sequence prepended with the specified values.
        """
        start = from_iterable(args)
        sequence = [start, source]
        return concat(*sequence)
    return start_with
