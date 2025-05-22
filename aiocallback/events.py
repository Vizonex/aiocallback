from __future__ import annotations

import types
import warnings
from functools import partial
from typing import (
    Any,
    Callable,
    Coroutine,
    Generic,
    MutableMapping,
    TypeVar,
    List,
    Iterable
)

from frozenlist import FrozenList
from typing_extensions import Concatenate, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")
OwnerT = TypeVar("OwnerT")

AsyncFunction = Callable[P, Coroutine[Any, Any, T]]


# EventWrapper is on par with aiosignal instead of being it's subclass
# This saves a couple of steps for many of our subclasses...


class EventWrapper(FrozenList[AsyncFunction[P, T]]):
    """A wrapper class for making a callback function that carries a few more methods than aiosignal has."""

    __slots__ = ("_owner",)

    def __init__(
        self,
        items: List[AsyncFunction[P, T]] | Iterable[AsyncFunction[P, T]] | None = None,
        /,
        owner=None,
    ):
        super().__init__(items)
        self._owner = owner

    def __call__(self, func: AsyncFunction[P, T]):
        """appends a callback function to the event, returns the same function for futher use elsewhere...
        this is equivilent to calling the `append()` method::

            from aiocallback import EventWrapper

            custom_event = EventWrapper()
            @custom_event
            async def on_event():
                ...

        """
        self.append(func)
        return func

    # Typehint our signal so that pyright can see
    # the arguments that need to be passed
    async def send(self, *args: P.args, **kw: P.kwargs) -> None:
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
    def __init__(self, items = None, /, owner=None):
        super().__init__(items, owner)


    async def send(self, *args: P.args, **kwargs: P.kwargs) -> None:
        return await super().send(self._owner, *args, **kwargs)  # type: ignore


class event(Generic[OwnerT, P, T]):
    """A Couroutine Based implementation of an asynchronous callback object. 
    This object is a replacement for aiosignal. with easier configuration options...
    
    abstract: `bool` inner function upon being called is considered abstract... \
        if `true` inner custom function will not be called with the `send()` method and it \
        will be considered as nothing but typehinting.
    """

    __slots__ = ("func", "name", "_wrapper")

    _wrapper: EventWrapper[P, T]

    def __init__(self, func: AsyncFunction[Concatenate[OwnerT, P], T], **kw) -> None:
        self.func = func
        self.name = func.__name__

        if hasattr(func, "__isabstractmethod__"):
            warnings.warn(
                "using an abc.abstractmethod wrapper with an event is discouraged",
                UserWarning,
                2,
            )

        # TODO: Remove in 0.1.6
        if kw.get("abstract"):
            warnings.warn(
                "abstract keyword is deprecated & it's functionality has been removed",
                DeprecationWarning,
                2,
            )

    # __doc__ couldn't be made into a slot
    # so we had to come up with an alternative method
    @property
    def __doc__(self):
        return self.func.__doc__

    def __wrapper_init__(self, owner: OwnerT):
        """A Special dunder method for initalizing an Event Wrapper"""
        self._wrapper = EventWrapper(owner=owner)
        return self._wrapper

    # Turns the event into a descriptor variable
    # SEE: https://docs.python.org/3/howto/descriptor.html
    # To sumarize it gets called during `__new__` which means that the wrapper 
    # will always attempt to be inbounds...
    def __set_name__(self, owner: OwnerT, name: str):
        self.__wrapper_init__(owner)
        self.name = name

    # inner _event_cache is removed because using slots on the descriptor is faster

    def __get__(self, inst: OwnerT, owner) -> EventWrapper[P, T]:
        # if for some reason we did not obtain this during __new__...
        if not hasattr(self, "_wrapper"):
            self.__wrapper_init__(owner)
        return self._wrapper

    __class_getitem__ = classmethod(types.GenericAlias)  # type:ignore


class subclassevent(event[OwnerT, P, T]):
    """Passes the context class to the member descriptor"""

    def __wrapper_init__(self, owner: OwnerT):
        self._wrapper = EventWrapper((partial(self.func, owner),), owner)
        return self._wrapper

    def __get__(self, inst: OwnerT, owner) -> EventWrapper[P, T]:
        # Incase the user's object does not have a base property to use...
        if not hasattr(self, "_wrapper") or self._wrapper._owner != inst:
            # Call the instance instead so that the instance is called with the event
            self.__wrapper_init__(inst)
        return self._wrapper


class contextevent(event[OwnerT, P, T]):
    """Sends the class holding the event through each of the callbacks made except for the wrapper itself. """

    _wrapper: SelfEventWrapper[P, T]

    def __wrapper_init__(self, owner: OwnerT):
        self._wrapper = SelfEventWrapper(owner=owner)
        return self._wrapper

    def __get__(self, inst: OwnerT, owner) -> SelfEventWrapper[P, T]:
        # Incase the user's object does not have a base property to use...
        if not hasattr(self, "_wrapper") or self._wrapper._owner != inst:
            self.__wrapper_init__(inst)
        return self._wrapper


class subcontextevent(contextevent):
    """sends the class holding the event as an instance through all the callbacks made including the inner wrapper
    being utilized."""

    def __wrapper_init__(self, owner):
        self._wrapper = SelfEventWrapper((self.func, ), owner)
        return self._wrapper

class subclasscontextevent(subcontextevent):
    def __init__(self, func, **kw):
        warnings.warn(
            "[Deprecated]: subclasscontextevent event has been renamed to subcontextevent (to try and lessen confusion), subclasscontextevent will be removed in 0.1.7",
            DeprecationWarning,
            2,
        )
        super().__init__(func, **kw)





# Inspired by PEP 3115's example
class event_table(dict):
    __slots__ = ("events",)
    events: dict[str, event | contextevent]
    def __init__(self):
        self.events = {}

    def __setitem__(self, key, value):
        # if the key is not already defined, add it to the
        # list of keys.
        if key not in self:
            # see if were either an event or context event.
            if isinstance(value, (event, contextevent)):
                self.events[key] = value

        # Call superclass
        dict.__setitem__(self, key, value)


# XXX: There's a problem with attrs accepting EventLists
# so there needs to be a workaround inplace in the future


class EventListMetaclass(type):
    """A Freezeable Metaclass for getting rid of 
   the need of freezing different member descriptors"""

    _events: dict[str, event]

    @classmethod
    def __prepare__(
        cls, name: str, bases: tuple[type, ...], /, **kw
    ) -> MutableMapping[str, object]:
        classdict = event_table()
        for b in bases:
            if isinstance(b, EventListMetaclass):
                for k, v in b._events.items():
                    if k in classdict.events:
                        raise ValueError(f"Event named {k} should only be defined once")
                    classdict.events[k] = v
        return classdict

    def __new__(cls, name: str, bases: tuple[type, ...], classdict: dict, /, **kw):
        # XXX: Attrs returns a real dictionary instead of our own by accident
        # Currently it's unknown as to why this happens
        if not isinstance(classdict, event_table):
            cd = cls.__prepare__(name, bases)
            cd.update(classdict)
            classdict = cd
        
        result = type.__new__(cls, name, bases, classdict, **kw)
        result._events = classdict.events  # type:ignore (classdict is actually event_table())
        return result


class EventList(metaclass=EventListMetaclass):
    """A Subclassable Helper for freezing up multiple callbacks together
    without needing to handle it all yourself"""

    _events: dict[str, event]

    @property
    def events(self) -> frozenset[str]:
        """An immutable set of event names attached to this class object"""
        return frozenset(self._events.keys())

    def freeze(self):
        """Freezes up all the different callback events
        that were configured"""
        for e in self._events.keys():
            # incase for some reason something is overwritten by the end developer
            object.__getattribute__(self, e).freeze()

