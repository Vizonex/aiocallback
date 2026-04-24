from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Generic, overload

from frozenlist import FrozenList
from propcache import under_cached_property as reify
from reductable_params import reduce
from reductable_params.abc import Reducable

from .typedefs import _P, _P2, _T

# Parent signal was made to be a customizable signal so a lot more error safety
# must be taken. However to get around this using self.signals directly
# in your own code is the perfect way to workaround any speed loss.


class ParentSignal(Generic[_P], FrozenList[Callable[..., Awaitable[object]]]):
    """A Parent signal takes it's given parameter specifications and
    creates an installation pattern for writing clean an beautiful callback
    systems."""

    __slots__ = ("_owner", "_cache", "_parent")

    def __init__(self, owner: object, parent: Callable[_P, Awaitable[object]]):
        super().__init__()
        self._owner = owner
        self._cache = {}
        self._parent = reduce(parent)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} owner={self._owner}, frozen={self.frozen}, {list(self)!r}>"

    # This signal data gets cached after first use in order
    # to not take super long.
    @reify
    def signals(self) -> FrozenList[Reducable[..., Awaitable[object]]]:
        """provides an immutable list of filterable callbacks.

        :raises TypeError: if signals are not frozen first."""
        if not self.frozen:
            raise TypeError("Can't make callbacks from non-frozen siganl.")
        signals = FrozenList(map(reduce, self))
        signals.freeze()
        return signals

    @reify
    def args(self) -> tuple[str, ...]:
        """lists required arguments as a tuple sequence."""
        return self._parent.args

    @reify
    def kwargs(self) -> tuple[str, ...]:
        """lists optional keyword arguments as tuple sequence."""
        return self._parent.kwargs

    @reify
    def name(self) -> str:
        """Return parent's original name"""
        return self._parent.__wrapped__.__name__

    def install(self, *args: _P.args, **kwargs: _P.kwargs) -> dict[str, Any]:
        """Prepares signal for sending the data.

        :raises TypeError: if arguments fail to parse.
        """
        return self._parent.install(*args, **kwargs)

    # Callables can be relaxed also with different kinds of function
    # signatures so we overload to define both kinds...
    @overload
    def __call__(
        self, func: Callable[_P, Coroutine[Any, Any, _T]]
    ) -> Callable[_P, Coroutine[Any, Any, _T]]: ...

    @overload
    def __call__(
        self, func: Callable[_P2, Coroutine[Any, Any, _T]]
    ) -> Callable[_P2, Coroutine[Any, Any, _T]]: ...

    def __call__(
        self,
        func: Callable[_P, Coroutine[Any, Any, _T]]
        | Callable[_P2, Coroutine[Any, Any, _T]],
    ) -> (
        Callable[_P, Coroutine[Any, Any, _T]]
        | Callable[_P2, Coroutine[Any, Any, _T]]
    ):
        """Wraps a callable coroutine to the signal."""
        self.append(func)
        return func

    async def send_packed(self, data: dict[str, Any]) -> None:
        """Sends data to all registered receievers as a packed dictionary.
        This can be exteremely useful when needing to customize the data
        before being sent.
        :raises RuntimeError: if signal is not frozen.
        """
        if not self.frozen:
            raise RuntimeError("Cannot send non-frozen signal.")

        for s in self.signals:
            await s(data)

    async def send(self, *args: _P.args, **kwargs: _P.kwargs) -> None:
        """Sends data to all regisered recievers.

        If you need data manipulation use `install(...)` with
        `send_packed(...)` instead.

        :raises RuntimeError: if signal is not frozen."""
        if not self.frozen:
            raise RuntimeError("Cannot send non-frozen signal.")

        data = self.install(*args, **kwargs)

        for s in self.signals:
            await s(data)
