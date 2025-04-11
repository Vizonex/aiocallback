from __future__ import annotations
from functools import partial
from typing import Dict, Generic, Protocol, TypeVar

from aiosignal import Signal
from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


class _TEvent(Protocol, Generic[T]):
    _event_cache: Dict[str, T]

    
class EventWrapper(Signal):
    """A wrapper class for making a callback function that carries a few more methods than aiosignal has."""

    def __call__(self, func):
        """appends a callback function to the event, returns the same function for futher use elsewhere...
        this is equivilent to calling the `append()` method::
            
            from aioevent import EventWrapper
            
            custom_event = EventWrapper()
            @custom_event
            async def on_event():
                ...


        """
        self.append(func)
        return func


class SelfEventWrapper(EventWrapper):
    """A wrapper class for making a callback that carries itself for use with each callback..."""

    async def send(self, *args, **kwargs) -> None:
        return await super().send(self._owner, *args, **kwargs)




class event:
    """A Couroutine Based implementation of an asynchronous callback object. 
    This object is a replacement for aiosignal. with easier configuration options...
    
    abstract: `bool` inner function upon being called is considered abstract... \
        if `true` inner custom function will not be called with the `send()` method and it \
        will be considered as nothing but typehinting.
    """

    def __init__(self, func, abstract: bool = True) -> None:
        self.func = func
        self.__doc__ = func.__doc__
        self.name = func.__name__
        self._abstract = abstract

    def __get__(self, inst, owner):
        # Incase the user's object does not have a base property to use...
        if getattr(inst, "_event_cache", None) is None:
            setattr(inst, "_event_cache", {})
        try:
            return inst._event_cache[self.name]
        except KeyError:
            val = EventWrapper(inst)
            inst._event_cache[self.name] = val
            if not self._abstract:
                # This doesn't pass a context normally so 
                # to bypass that for a class method we have to do this...
                val.append(partial(self.func, inst))
            return val
        except AttributeError:
            if inst is None:
                return self
            raise


def subclassevent(func):
    """Turns off abstract functions allowing inner functions to be events"""
    return event(func, abstract=False)


class contextevent:
    """An event who's callback Carries the class object as a context to be used with the event...
    
    abstract: `bool` inner function upon being called is considered abstract... \
        if `true` inner custom function will not be called with the `send()` method and it \
        will be considered as nothing but typehinting."""

    def __init__(self, func, abstract: bool = True) -> None:
        self.func = func
        self.__doc__ = func.__doc__
        self.name = func.__name__
        self._abstract = abstract

    def __get__(self, inst: _TEvent[SelfEventWrapper], owner):
        if getattr(inst, "_event_cache", None) is None:
            setattr(inst, "_event_cache", {})
        try:
            return inst._event_cache[self.name]
        except KeyError:
            val = SelfEventWrapper(inst)
            inst._event_cache[self.name] = val

            if not self._abstract:
                val.append(self.func)
            return val
        except AttributeError:
            if inst is None:
                return self
            raise


def subclasscontextevent(func):
    """Turns off abstract functions allowing inner functions to be events"""
    return contextevent(func, abstract=False)




# Inspired by PEP 3115's example
class event_table(dict):
    def __init__(self):
        self.events:dict[str, event | contextevent] = {}

    def __setitem__(self, key, value):
        # if the key is not already defined, add to the
        # list of keys.
        # print((key,value))
        if key not in self:
            # print((key,value))
            # see if were either an event or context event.
            if isinstance(value, (event, contextevent)):
                self.events[key] = value

        # Call superclass
        dict.__setitem__(self, key, value)


class EventListMetaclass(type):
    """A Freezeable Metaclass for getting rid of unneeded boilerplate code when needing to 
    freeze mulitple functions tied to one class"""

    @classmethod
    def __prepare__(cls, name:str, bases:tuple[type, ...]):
        return event_table()
    
    def __new__(cls, name, bases, classdict):
        for b in bases:
            if isinstance(b, EventListMetaclass):
                for k, v in b._events.items():
                    if k in classdict.events:
                        raise ValueError(f"Event named {k} should only be defined once")
                    classdict.events[k] = v

        result = type.__new__(cls, name, bases, dict(classdict))
        result._events = classdict.events
        return result


class EventList(metaclass=EventListMetaclass):
    """A Subclassable Helper for freezing up multiple callbacks together without needing to handle it all yourself"""

    @property
    def events(self) -> frozenset[str]:
        """An immutable set of event names attached to this class object"""
        return frozenset(self._events.keys())

    def freeze(self):
        """Freezes up all the different callback events 
        that were configured"""
        for e in self._events.keys():
            # print(e)
            # incase for some reason something is overwritten by the end developer
            object.__getattribute__(self, e).freeze()



    

