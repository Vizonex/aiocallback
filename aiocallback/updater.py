"""Polls different objects to find new differences. When a difference is found
object updates."""

import inspect
from collections.abc import (
    AsyncGenerator,
    AsyncIterable,
    Awaitable,
    Callable,
    Hashable,
    Iterable,
    Sequence,
)
from contextlib import asynccontextmanager
from enum import IntEnum, auto
from functools import _make_key
from types import TracebackType
from typing import Any, Generic, overload

from .signals import ParentSignal
from .typedefs import _K, _P, _T, _V, Self

# TODO: (Seperate Cache) into it's own little library in a later update.
# Might also be possible to cythonize it's code for even greater speeds.


# Easier to read than a boolean would provide for us.
class ItemType(IntEnum):
    """Observed Object Type. Defines which set of items the being observed belong to."""

    NEW = auto()
    OLD = auto()


class Cache(Generic[_K]):
    """Helps observe new and old items coming in and out of iteself.
    This LRU method is based on a 2 group system that clears itself
    based on a un-provided max-amount of entries.
    """

    # This cache object can prevent problems when needing to load
    # a random amount of entries on a page where page 1 may contain
    # 20 entries many moments later maybe the next referesh 30.
    # Those 10 differences need to be captured but also unseen entries moving
    # to page 2 maybe considered unimportant. Old entries can then reset
    # and never see page 2 (which is what we want to happen) so that memory
    # never has the chance of overflowing with older entries.

    __slots__ = ("_cache",)

    def __init__(self) -> None:
        # This can be slightly faster than utilizing 2 different sets
        # As both need to be checked to prevent older entries from past 
        # sessions from leaking out and then reappearing.
        # Groups are marked via value either marked as NEW or OLD
        self._cache: dict[_K, ItemType] = {}

    def __contains__(self, item: _K) -> bool:
        """Checks both new and old entries to see if this target item has been observed previously.
        This prevents data from previously seen and currently seen from being clustered."""
        return item in self._cache

    def add(self, item: _K) -> None:
        """Sets item observed as being a new entry for the remainder of it's session until reset.

        :param item: the new item to mark as being a newer entry.
        """
        self._cache[item] = ItemType.NEW

    def reset(self) -> None:
        """Cleans up previously seen data and marks newly seen data as part of an older set.
        If there are no entries that are seen as new. Cache will not be updated if there are 
        no newer entries."""

        # Confusing wording but basically if there are no new entries then it's not a good 
        # idea update the cache.
        self._cache = {
            k: ItemType.OLD
            for k, v in self._cache.items()
            if v == ItemType.NEW
        } or self._cache

    def clear(self) -> None:
        """Clears all entries in the cache. All entries will be forgotten about."""
        self._cache.clear()

    def keys(self) -> set[_T]:
        """useful when debugging the cache to see what kinds of items are used."""
        return set(self._cache.keys())


class Updater(Generic[_T]):
    """An object listener that scans for new objects.
    When a new object is found, a callback is triggered.

    It can be used in repeat succession when used as
    context-manager. It is mainly meant for small or
    medium sized amounts of traffic to inspect.
    """

    __slots__ = ("_cache", "_cb")

    def __init__(self, on_update: Callable[[_T], Awaitable[None]]) -> None:
        """
        :param on_update: an asynchronous callback to provide
        """
        self._cb = on_update
        # memory optimization was to store the hash instead of the object
        # this saves memory and also allows for a mutating object to be
        # considered a valid entry if it comes back as being not the same.
        self._cache: Cache[Hashable] = Cache()

    def reset(self) -> None:
        """Clears currently seen and stores it as previously seen data."""
        self._cache.reset()

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

    def __hash_item__(self, item: _T) -> Hashable | int:
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
        if _hash not in self._cache:
            await self._cb(item)
        # Store item so that it isn't called again in this checked session.
        self._cache.add(_hash)

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

    def __hash_item__(self, item: dict[_K, _V]) -> Hashable:
        return _make_key((), kwds=item, typed=True)


class UpdateSignal(ParentSignal[_P]):
    """Searches for unique elements before being allowed to send them."""

    __slots__ = ("_cache", "_owner", "_parent", "_updater")

    def __init__(
        self, owner: object, parent: Callable[_P, Awaitable[object]]
    ) -> None:
        super().__init__(owner, parent)
        self._updater: MapUpdater[str, Any] = MapUpdater(self.notify)

    async def notify(self, data: dict[str, Any]) -> None:
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
    async def automatic(self) -> AsyncGenerator[None, None]:
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
        items: Sequence[_T] | Iterable[_T] | AsyncGenerator[_T, Any],
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
        self, items: Sequence[Any] | Iterable[Any] | AsyncGenerator[Any, Any]
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
        self, items: Sequence[Any] | Iterable[Any] | AsyncGenerator[Any, Any]
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
