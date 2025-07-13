from __future__ import annotations

import sys
import types
import warnings
from functools import partial
from typing import (
    Any,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    List,
    MutableMapping,
    TypeVar,
)

from frozenlist import FrozenList
from propcache import under_cached_property

if sys.version_info >= (3, 10):
    from typing import Concatenate, ParamSpec
else:
    from typing_extensions import Concatenate, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")
OwnerT = TypeVar("OwnerT")

AsyncFunction = Callable[P, Coroutine[Any, Any, T]]

__all__ = (
    "EventList",
    "EventListMetaclass",
    "EventWrapper",
    "SelfEventWrapper",
    "contextevent",
    "event",
    "subcontextevent",
    "subclassevent",
)

# EventWrapper is inspired by aiosignal but has a few internal
# changes made to make it more beginner-friendly.


class EventWrapper(FrozenList[AsyncFunction[P, T]]):
    """A wrapper class for making a callback function that carries
    a few more methods than aiosignal has. What makes EventWrapper
    different from aiosignal is that it utilizes ParamSpec. This can
    have an advantage when you need to typehint multiple different
    functions, positonal and keyword arguments.
    """

    __slots__ = ("_owner",)

    def __init__(
        self,
        items: List[AsyncFunction[P, T]] | Iterable[AsyncFunction[P, T]] | None = None,
        /,
        owner: Any | None = None,
    ):
        """
        Parameters
        ----------

        :param owner: Simillar to `aiosignal.Signal` using an owner is entirely optional but encouraged
        :param items: A list or sequence of funtions to utilize.

        """
        super().__init__(items)
        self._owner = owner

    def __call__(self, func: AsyncFunction[P, T]):
        """
        appends a callback function to the event, returns the same function for futher use elsewhere...
        this is equivilent to calling the `append()` method::

            from aiocallback import EventWrapper

            custom_event = EventWrapper()
            @custom_event
            async def on_event():
                ...

        Parameters
        ----------

        :param func: the function that should get called back to when the event is invoked

        """
        self.append(func)
        return func

    # Typehint our signal so that pyright can see
    # the arguments that need to be passed
    async def send(self, *args: P.args, **kw: P.kwargs) -> None:
        """
        Sends Parameters to invoke all functions tied to this event.
        """
        if not self.frozen:
            raise RuntimeError("Cannot send non-frozen events.")

        for receiver in self:
            await receiver(*args, **kw)  # type: ignore

    def __repr__(self):
        return "<{} owner={}, frozen={}, {!r}>".format(
            self.__class__.__name__, self._owner, self.frozen, list(self)
        )


class SelfEventWrapper(EventWrapper[P, T]):
    """A wrapper class for making an owner object sendable with all the events"""

    def __init__(self, items=None, /, owner=None):
        super().__init__(items, owner)

    async def send(self, *args: P.args, **kwargs: P.kwargs) -> None:
        return await super().send(self._owner, *args, **kwargs)  # type: ignore


class event(Generic[OwnerT, P, T]):
    """A Couroutine Based implementation of an asynchronous callback object.
    This object is a replacement for aiosignal. with easier configuration options...
    """

    __slots__ = ("_func", "_name", "_wrapper", "_cache")
    _wrapper: EventWrapper[P, T]

    def __init__(self, func: AsyncFunction[Concatenate[OwnerT, P], T], **kw) -> None:
        self._func = func
        self._name = func.__name__
        self._cache: dict[str, Any] = {}

        if hasattr(func, "__isabstractmethod__"):
            warnings.warn(
                "using an abc.abstractmethod wrapper with an event is discouraged"
                "this will throw an error in a future version of aiocallback!",
                UserWarning,
                2,
            )

    # XXX: __doc__ couldn't be made into a slot
    # so we had to come up with an alternative method
    @under_cached_property
    def __doc__(self):
        return self._func.__doc__

    def __wrapper_init__(self, owner: OwnerT):
        """
        A Special dunder method for initalizing an Event Wrapper

        Parameters
        ----------

        :param owner: the owning class object that will maintain the events called
        """
        self._wrapper = EventWrapper(owner=owner)
        return self._wrapper

    # Turns the event into a descriptor variable
    # SEE: https://docs.python.org/3/howto/descriptor.html
    # To sumarize it gets called during `__new__` which means that the wrapper
    # will always attempt to be inbounds...
    def __set_name__(self, owner: OwnerT, name: str):
        self.__wrapper_init__(owner)
        self._name = name

    # inner _event_cache is removed because using slots on the descriptor is faster

    def __get__(self, inst: OwnerT, owner: OwnerT) -> EventWrapper[P, T]:
        # if for some reason we did not obtain this during __new__...
        if not hasattr(self, "_wrapper"):
            self.__wrapper_init__(owner)
        return self._wrapper

    __class_getitem__ = classmethod(types.GenericAlias)  # type:ignore


class subclassevent(event[OwnerT, P, T]):
    """Passes the context class to the member descriptor"""

    def __wrapper_init__(self, owner: OwnerT) -> EventWrapper[P, T]:
        self._wrapper = EventWrapper((partial(self._func, owner),), owner)
        return self._wrapper

    def __get__(self, inst: OwnerT, owner: Any) -> EventWrapper[P, T]:
        # Incase the user's object does not have a base property to use...
        if not hasattr(self, "_wrapper") or self._wrapper._owner != inst:
            # Call the instance instead so that the instance is called with the event
            self.__wrapper_init__(inst)
        return self._wrapper


class contextevent(event[OwnerT, P, T]):
    """Sends the class holding the event through each of the callbacks made except for the wrapper itself."""

    _wrapper: SelfEventWrapper[P, T]

    def __wrapper_init__(self, owner: OwnerT):
        self._wrapper = SelfEventWrapper(owner=owner)
        return self._wrapper

    def __get__(
        self, inst: OwnerT, owner: Any
    ) -> SelfEventWrapper[P, T]:
        # Incase the user's object does not have a base property to use...
        if not hasattr(self, "_wrapper") or self._wrapper._owner != inst:
            self.__wrapper_init__(inst)
        return self._wrapper


class subcontextevent(contextevent[OwnerT, P, T]):
    """sends the class holding the event as an instance through all the callbacks made including the inner wrapper
    being utilized."""

    def __wrapper_init__(self, owner: OwnerT) -> SelfEventWrapper:
        self._wrapper = SelfEventWrapper((self._func,), owner)
        return self._wrapper


# Inspired by PEP 3115's example
class event_table(dict):
    __slots__ = ("events",)

    def __init__(self):
        self["_events"] = {}

    def __setitem__(self, key: str, value: Any):
        # if the key is not already defined, add it to the
        # list of keys.
        if key not in self:
            # see if were either an event or context event.
            if isinstance(value, (event, contextevent)):
                self["_events"][key] = value

        # Call superclass
        dict.__setitem__(self, key, value)


# XXX: There's a problem with attrs accepting EventLists
# so there needs to be a workaround inplace in the future


class EventListMetaclass(type):
    """A Freezeable Metaclass for freezing wrapped events in a class object"""

    _events: dict[str, event]

    # EventLists fully support popcache's under_cached_property
    # if user wants to use it to make immutable properties
    _cache: dict[str, Any]

    @classmethod
    def __prepare__(
        cls, name: str, bases: tuple[type, ...], /, **kw
    ) -> MutableMapping[str, object]:
        classdict = event_table()
    
        for b in bases:
            if isinstance(b, EventListMetaclass):
                classdict["_events"].update(b._events)
    
        classdict["_cache"] = {}
        return classdict

    def __new__(cls, name: str, bases: tuple[type, ...], classdict: dict, /, **kw):
        return type.__new__(cls, name, bases, classdict, **kw)


class EventList(metaclass=EventListMetaclass):
    """A Subclassable Helper for freezing up multiple callbacks together
    without needing to handle it all yourself"""
    _events: dict[str, Any]
    _cache: dict[str, Any]


    @under_cached_property
    def events(self) -> frozenset[str]:
        """An immutable set of event names attached to this class object"""
        return frozenset(self._events.keys())

    # TODO: Should Freeze be single-dispatch in the future?
    def freeze(self) -> None:
        """Freezes up all the different callback events
        that were configured"""
        for e in self._events.keys():
            # incase for some reason something is overwritten by the end developer
            object.__getattribute__(self, e).freeze()
