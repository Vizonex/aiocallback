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
            this is equivilent to calling the `append()` method
        ::

            from aioevent import EventWrapper

            custom_event = EventWrapper()

            @custom_event
            async def on_event():
                ...
        ::

        """
        self.append(func)
        return func


class SelfEventWrapper(EventWrapper):
    """A wrapper class for making a callback that carries itself for use with each callback..."""

    async def send(self, *args, **kwargs) -> None:
        return await super().send(self._owner, *args, **kwargs)


# def freeze_events(base: _TEvent[Union[SelfEventWrapper, EventWrapper]]):
#     """Freezes all events for a base context object for making events easier to serlize
#     before beginning to use the inner signals for different callbacks"""
#     for v in property.base:
#         if isinstance(v, EventWrapper):
#             v.freeze()


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
