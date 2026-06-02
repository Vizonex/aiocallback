"""Polls different objects to find new differences. When a difference is found
object updates."""

import inspect
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Iterable,
    Sequence,
)
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Any, Generic, overload

from .signals import ParentSignal
from .typedefs import _K, _P, _T, _V, Self


class Updater(Generic[_T]):
    """An object listener that scans for new objects.
    When a new object is found, a callback is triggered.

    It can be used in repeat succession when used as
    context-manager. It is mainly meant for small or
    medium sized amounts of traffic to inspect.
    """

    __slots__ = ("_current", "_previous", "_cb")

    def __init__(self, on_update: Callable[[_T], Awaitable[None]]) -> None:
        """
        :param on_update: an asynchronous callback to provide
        """
        self._cb = on_update
        # memory optimization was to store the hash instead of the object
        # this saves memory and also allows for a mutating object to be
        # considered a valid entry if it comes back as being not the same.
        self._current: set[int] = set()
        self._previous: set[int] = set()

    def reset(self) -> None:
        """Clears currently seen and stores it as previously seen data."""
        self._previous.clear()
        self._previous.update(self._current)
        self._current.clear()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """closes the newly updated cycle calling `reset(...)` for you."""
        self.reset()

    def __hash_item__(self, item: _T) -> int:
        """Hashes item that needs checking.
        This allows for extended manipulation and subclassing"""
        return hash(item)

    async def check(self, item: _T) -> None:
        """
        Checks a single item to see if it's considered new. If it is new,
        then the callback is updated.

        :param item: the item to inspect
        """
        # storing the hash instead of the value itself prevents performance regressions...
        _hash = self.__hash_item__(item)
        if (_hash not in self._current) and (_hash not in self._previous):
            await self._cb(item)
        # Store item so that it isn't called in this checked session.
        self._current.add(_hash)

    async def poll(
        self, items: Sequence[_T] | Iterable[_T] | AsyncIterable[_T, Any]
    ) -> None:
        """
        Polls a group of items while resetting the seen items
        afterwards, the items can be iterated both normally
        or asynchronously.

        :param items: the items or iterator of items to inspect...
        """
        async with self:
            if inspect.isasyncgen(items):
                async for i in items:
                    await self.check(i)
            else:
                for i in items:
                    await self.check(i)


class MapUpdater(Updater[dict[_K, _V]]):
    """Observes updates from a dictionary"""

    def __hash_item__(self, item: dict[_K, _V]):
        return hash(tuple(sorted(item.items())))


class UpdateSignal(ParentSignal[_P]):
    """Searches for unique elements before being allowed to send them."""

    __slots__ = ("_owner", "_cache", "_parent", "_updater")

    def __init__(self, owner: object, parent: Callable[_P, Awaitable[object]]):
        super().__init__(owner, parent)
        self._updater: MapUpdater[str, Any] = MapUpdater(self.notify)

    async def notify(self, data: dict[str, Any]):
        """Notifies updater that a new object is now ready.
        This is mostly an injectable function incase user needs to
        subclass off :class:`UpdateSignal` and provide hooks and
        other tooling for further parameter manipulation.

        :param data: data to send.

        :raises RuntimeError: if signal is not frozen.
        """
        if not self.frozen:
            raise RuntimeError("Cannot send non-frozen signal.")

        for s in self.signals:
            await s(data)

    @asynccontextmanager
    async def automatic(self) -> AsyncIterator[None]:
        """Performs restting of the updater automatically
        as an asyncrhonous context-manager. On exit
        all items that were registered on the previous cycle
        are cleared and the ones that were seen after this cycle
        are kept.

        :raises RuntimeError: if signal is not frozen."""
        if not self.frozen:
            raise RuntimeError("Cannot update using a non-frozen signal.")

        async with self._updater:
            yield

    def reset(self) -> None:
        """Clears currently seen and stores it as previously seen data."""
        return self._updater.reset()

    async def update(self, *args: _P.args, **kwargs: _P.kwargs) -> None:
        """
        checks a group of objects to see if they are considered
        unqiue before sending them...

        :raises RuntimeError: if signal is not frozen.
        """
        if not self.frozen:
            raise RuntimeError("Cannot update non-frozen signal.")

        await self._updater.check(self.install(*args, **kwargs))

    @overload
    async def poll(
        self: "UpdateSignal[_T]",
        items: Sequence[_T] | Iterable[_T] | AsyncIterable[_T, Any],
    ) -> None:
        """Polls items into :function:`.update()`.

        Disadvantages
        -------------
        Weaknesses with this function include lack blanaced typehinting
        due to how paramspec works.

        Advantages
        ----------
        This function can provide massive code optimizations for the end user
        if iterators are needed but we want to minimize the amount
        of code being written.

        :raises RuntimeError: if signal is not frozen
        """

    @overload
    async def poll(
        self, items: Sequence[Any] | Iterable[Any] | AsyncIterable[Any, Any]
    ) -> None:
        """Polls items into :function:`.update()`.

        Disadvantages
        -------------
        Weaknesses with this function include lack blanaced typehinting
        due to how paramspec works.

        Advantages
        ----------
        This function can provide massive code optimizations for the end user
        if iterators are needed but we want to minimize the amount
        of code being written.

        :raises RuntimeError: if signal is not frozen
        """

    async def poll(
        self, items: Sequence[Any] | Iterable[Any] | AsyncIterable[Any, Any]
    ) -> None:
        """Polls items into :function:`.update()`.

        Disadvantages
        -------------
        Weaknesses with this function include lack blanaced typehinting
        due to how paramspec works.

        Advantages
        ----------
        This function can provide massive code optimizations for the end user
        if iterators are needed but we want to minimize the amount
        of code being written.

        :raises RuntimeError: if signal is not frozen
        """
        if not self.frozen:
            raise RuntimeError("Cannot update non-frozen signal.")

        async with self.automatic():
            if inspect.isasyncgen(items):
                async for i in items:
                    await self._updater.check(self.install(i))
            else:
                for i in items:
                    await self._updater.check(self.install(i))
