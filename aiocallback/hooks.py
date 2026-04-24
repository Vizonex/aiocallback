from __future__ import annotations

import inspect
from collections.abc import AsyncIterator, Callable
from contextlib import (
    AbstractAsyncContextManager,
    AsyncExitStack,
    asynccontextmanager,
)

from freezabledict import FrozenDict

from .typedefs import Unpack, _Ts


def is_asynccontextmanagerfunction(obj: object) -> bool:
    """Attempts to see if object is possibly wrapped with an asynccontextmanager
    wrapper or not"""
    return (
        inspect.isasyncgenfunction(obj.__wrapped__)
        if hasattr(obj, "__wrapped__")
        else False
    )


class Hook(
    FrozenDict[
        str, Callable[[Unpack[_Ts]], AbstractAsyncContextManager[object]]
    ]
):
    """Hook for calling back multiple context manager-like fixtures"""

    def __init__(self, owner: object) -> None:
        super().__init__()
        self._owner = owner

    def __repr__(self):
        return f"<{self.__class__.__name__}(frozen={self._frozen}, owner={self._owner}, {self._items!r})"

    @asynccontextmanager
    async def send(
        self, *args: Unpack[_Ts], **kwargs
    ) -> AsyncIterator[dict[str, object]]:
        """Sends all life-cycles and returns them for use elsewhere as a
        dictionary object"""
        if not self.frozen:
            raise RuntimeError("Cannot enter into non-frozen life-cycle.")

        async with AsyncExitStack() as s:
            yield {
                name: await s.enter_async_context(cm(*args, **kwargs))
                for name, cm in self.items()
            }
