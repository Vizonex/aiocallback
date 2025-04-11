from typing import Any, Awaitable, Callable, Dict, Generic, Protocol, TypeVar

from aiosignal import Signal
from typing_extensions import Concatenate, ParamSpec

# Typehints to fix some functionailty in of some different coding ides...

T = TypeVar("T")
P = ParamSpec("P")
_TOwner = TypeVar("_TOwner")

class _TEvent(Generic[T], Protocol):
    _event_cache: Dict[str, T]

class EventWrapper(Signal[Callable[P, Awaitable[T]]], Generic[P, T]):
    def __call__(
        self, func: Callable[P, Awaitable[T]]
    ) -> Callable[P, Awaitable[T]]: ...
    async def send(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def freeze(self) -> None: ...

class SelfEventWrapper(EventWrapper[P, T], Generic[_TOwner, P, T]):
    def __call__(
        self, func: Callable[Concatenate[_TOwner, P], Awaitable[T]]
    ) -> Callable[Concatenate[_TOwner, P], Awaitable[T]]: ...
    async def send(self, *args: P.args, **kwargs: P.kwargs) -> None: ...


# These are mainly used to bypass the actual class wrapper methods so that typehinting works correctly

# TODO: Fix abstract argument typehinting (flipping it to false ruins typehinting...)

def event(
    func: Callable[Concatenate[Any, P], Awaitable[T]], abstract: bool = True
) -> EventWrapper[P, T]:
    """A Couroutine Based implementation of an asynchronous callback object. 
    This object is a replacement for aiosignal. with easier configuration options...
    
    abstract: `bool` inner function upon being called is considered abstract... \
        if `true` inner custom function will not be called with the `send()` method and it \
        will be considered as nothing but typehinting. default is `true`
    """

def subclassevent(
    func: Callable[Concatenate[Any, P], Awaitable[T]],
) -> EventWrapper[P, T]: ...
def contextevent(
    func: Callable[Concatenate[_TOwner, P], Awaitable[T]], abstract: bool = True
) -> SelfEventWrapper[_TOwner, P, T]:
    """An event who's callback Carries the class object as a context to be used with the event...
    
    abstract: `bool` inner function upon being called is considered abstract... \
        if `true` inner custom function will not be called with the `send()` method and it \
        will be considered as nothing but typehinting. default is `true`"""

def subclasscontextevent(
    func: Callable[Concatenate[_TOwner, P], Awaitable[T]],
) -> EventWrapper[P, T]: ...


class EventListMetaclass(type):
    """A Freezeable Metaclass for getting rid of unneeded boilerplate code when needing to 
    freeze mulitple functions tied to one class"""

class EventList(metaclass=EventListMetaclass):
    """A Subclassable Helper for freezing up multiple callbacks together without needing to handle it all yourself"""
    # _events:ClassVar[dict[str, event | contextevent]]

    def freeze(self) -> None:
        """Freezes up the different callback events that were configured"""
    @property
    def events(self) -> frozenset[str]:...
