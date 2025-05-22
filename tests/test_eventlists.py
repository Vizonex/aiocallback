import asyncio
import sys
from dataclasses import dataclass

import pytest
import pytest_asyncio

from aiocallback.events import (EventList, contextevent, event, subclassevent,
                                subcontextevent)

try:
    import attrs
    ATTRS_NOT_FOUND = False
except ModuleNotFoundError:
    ATTRS_NOT_FOUND = True


try:
    # As much as you should try migrating to using msgspec
    # until pydantic decides to migrate it's 
    # metaclass BaseModel to C / Cython / Rust
    # I shall do my fair share of trying to support it.
    import pydantic
    PYDANTIC_NOT_FOUND = False
except ModuleNotFoundError:
    PYDANTIC_NOT_FOUND = True


try:
    import msgspec
    MSGSPEC_NOT_FOUND = False
except ModuleNotFoundError:
    MSGSPEC_NOT_FOUND = True


attrs_test = pytest.mark.skipif(
    ATTRS_NOT_FOUND, reason="Attrs Not Found!"
)

pydantic_test = pytest.mark.skipif(
    PYDANTIC_NOT_FOUND, reason="Pydantic Not Found!"
)

msgspec_test = pytest.mark.skipif(
    MSGSPEC_NOT_FOUND, reason="Msgspec Not Found!"
)



@pytest.mark.asyncio
async def test_eventlist_freezing():
    
    class MyEvents(EventList):
        @event
        async def my_event_1(self):
            pass
        
        @contextevent
        async def my_event_2(self):
            pass

        @subclassevent
        async def my_event_3(self):
            pass

        @subcontextevent
        async def my_event_4(self):
            pass
    
    my_events = MyEvents()
    my_events.freeze()
    for e in my_events.events:
        assert getattr(my_events, e).frozen, f"{e} did not freeze"


# This is what EventLists were invented for
# - Lazy setting
# - Lazy Initialization
#
# With dataclass support added and now with attrs support, 
# you can get as lazy as you want.

@pytest.mark.asyncio
async def test_dataclass_eventlist_support():
    @dataclass
    class MyEvents(EventList):
        x: int = 0
        y: int = 0
        @event
        async def my_event_1(self):
            pass
        
        @contextevent
        async def my_event_2(self):
            pass

        @subclassevent
        async def my_event_3(self):
            pass

        @subcontextevent
        async def my_event_4(self):
            pass
    
    e = MyEvents(1, 2)
    assert e.x == 1
    assert e.y == 2


@attrs_test
@pytest.mark.asyncio
async def test_attrs_eventlist_support():
   
    @attrs.define
    class MyEvents(EventList):
        x: int = 0
        y: int = 0
        @event
        async def my_event_1(self):
            pass
        
        @contextevent
        async def my_event_2(self):
            pass

        @subclassevent
        async def my_event_3(self):
            pass

        @subcontextevent
        async def my_event_4(self):
            pass
    
    e = MyEvents(1, 2)
    assert e.x == 1
    assert e.y == 2


@pydantic_test
@pytest.mark.asyncio
async def test_pydantic_eventlist_support():
   
    @pydantic.dataclasses.dataclass
    class MyEvents(EventList):
        x: int = 0
        y: int = 0
        @event
        async def my_event_1(self):
            pass
        
        @contextevent
        async def my_event_2(self):
            pass

        @subclassevent
        async def my_event_3(self):
            pass

        @subcontextevent
        async def my_event_4(self):
            pass
    
    e = MyEvents(1, 2)
    assert e.x == 1
    assert e.y == 2


@msgspec_test
@pytest.mark.asyncio
async def test_msgspec_struct_support():
    # I don't expect msgspec to support 
    # Eventlists yet since it has strict rules about what goes into 
    # it and out of it.

    # Until Msgspec's StructMeta Class Object is Publically Exposed 
    # I don't Expcet us supporting it anytime soon...

    # However we can test if at least one event will freeze

    class MyEvents(msgspec.Struct, dict=False):
        x:int = 0
        y:int = 0

        @event
        async def my_event_1(self):
            pass

    e = MyEvents(1, 2)
    assert e.x == 1
    assert e.y == 2

    e.my_event_1.freeze()
    assert e.my_event_1.frozen, "msgspec.Struct did not freeze the event"


    
