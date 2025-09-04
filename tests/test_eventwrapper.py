import random

import pytest

from aiocallback.events import (
    EventWrapper,
    contextevent,
    event,
    subclassevent,
    subcontextevent,
    defaultevent,
    subdefaultevent
)


def compute_result():
    """Simple addition function test"""
    a, b = random.choices([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], k=2)
    result = a + b
    return result, a, b


def random_value():
    return random.randint(0, 5000)


@pytest.mark.asyncio
async def test_eventwrapper():
    # Fun fact: You can typehint EventWrapper as a Callable, isn't that just neat?
    add_event: EventWrapper[[int, int], None] = EventWrapper()

    result, a, b = compute_result()

    @add_event
    async def on_add(a: int, b: int):
        nonlocal result
        assert a + b == result, (
            f"on_add did not send {a}+{b} correctly and got {result}"
        )

    add_event.freeze()
    await add_event.send(a, b)


@pytest.mark.asyncio
async def test_eventwrapper_member_descriptor():
    result, a, b = compute_result()

    class TestEvent:
        @event
        async def on_add(self, a: int, b: int) -> None:  # type: ignore
            raise RuntimeError("on_add disallows internal calling")

    test_event = TestEvent()

    async def run_test(a: int, b: int):
        nonlocal result
        assert a + b == result, (
            f"on_add event did not send {a}+{b} correctly and got {result}"
        )

    @test_event.on_add
    async def generic_on_add(a: int, b: int):
        await run_test(a, b)

    # Test appending an event
    async def on_add_append(a: int, b: int):
        await run_test(a, b)

    test_event.on_add.append(on_add_append)

    assert generic_on_add in test_event.on_add, "generic_on_add was not added"
    assert on_add_append in test_event.on_add, "on_add_append was not added"

    test_event.on_add.freeze()
    assert test_event.on_add.frozen, "on_add is not frozen"
    await test_event.on_add.send(a, b)


@pytest.mark.asyncio
async def test_eventwrapper_subclass_memeber_descriptor():
    class TestSubclassEvent:
        def __init__(self):
            self.event_called = False

        @subclassevent
        async def subcls_event(self, value: int):
            assert hasattr(self, "event_called"), (
                "TestSubclassEvent Was initalized the wrong way."
            )
            self.event_called = True

    test_sub_event = TestSubclassEvent()

    assert not test_sub_event.event_called, (
        "event_called wasn't called yet but was flagged as true"
    )

    SHOULDVE_CALLED_FOR = random_value()

    @test_sub_event.subcls_event
    async def on_subclass_called(value: int):
        nonlocal SHOULDVE_CALLED_FOR
        assert SHOULDVE_CALLED_FOR == value, (
            "SHOULDVE_CALLED_FOR WAS INCORRECT Value:{!r}".format(value)
        )

    assert on_subclass_called in test_sub_event.subcls_event, "callback wasn't given"

    test_sub_event.subcls_event.freeze()

    await test_sub_event.subcls_event.send(SHOULDVE_CALLED_FOR)

    assert test_sub_event.event_called, "subcls_event Was not Called"


@pytest.mark.asyncio
async def test_eventwrapper_contextevent():
    class TestContextEvent:
        def __init__(self):
            self.event_called = False

        @contextevent
        async def subcls_event(self, _: int) -> None:  # type: ignore
            raise RuntimeError("class's inner event wasn't ignored")

    test_sub_event = TestContextEvent()

    assert not test_sub_event.event_called, (
        "event_called wasn't called yet but was flagged as true"
    )

    SHOULDVE_CALLED_FOR = random_value()

    @test_sub_event.subcls_event
    async def on_subclass_called(event: TestContextEvent, value: int):
        assert hasattr(event, "event_called"), (
            "instanced of the event should've been passed"
        )

        nonlocal SHOULDVE_CALLED_FOR
        assert SHOULDVE_CALLED_FOR == value, (
            'SHOULDVE_CALLED_FOR WAS INCORRECT, "Value Passed":{!r}'.format(value)
        )

    assert on_subclass_called in test_sub_event.subcls_event, (
        "subclassevent member descriptor had an attribute problem"
    )
    test_sub_event.subcls_event.freeze()
    await test_sub_event.subcls_event.send(SHOULDVE_CALLED_FOR)
    assert not test_sub_event.event_called, (
        "Event Shouldn't have been set to begin with"
    )


@pytest.mark.asyncio
async def test_eventwrapper_subcontextevent():
    class TestSubContextEvent:
        def __init__(self):
            self.event_called = False

        @subcontextevent
        async def subcls_event(self, _: int) -> None:  # type: ignore
            assert hasattr(self, "event_called"), (
                "TestSubContextEvent Was initalized the wrong way."
            )
            self.event_called = True

    test_sub_event = TestSubContextEvent()

    assert not test_sub_event.event_called, (
        "event_called wasn't called yet but was flagged as true"
    )

    SHOULDVE_CALLED_FOR = random_value()

    @test_sub_event.subcls_event
    async def on_subclass_called(event: TestSubContextEvent, value: int):
        assert hasattr(event, "event_called"), (
            "instance of this event should've been passed"
        )

        nonlocal SHOULDVE_CALLED_FOR
        assert SHOULDVE_CALLED_FOR == value, (
            'SHOULDVE_CALLED_FOR WAS INCORRECT, "Value Passed":{!r}'.format(value)
        )

    assert on_subclass_called in test_sub_event.subcls_event, (
        "subclassevent member descriptor had an attribute problem"
    )
    test_sub_event.subcls_event.freeze()
    await test_sub_event.subcls_event.send(SHOULDVE_CALLED_FOR)

    assert test_sub_event.event_called, "Inner function was not called"


@pytest.mark.asyncio
async def test_default_event():

    class TestDefaultEvent:
        def __init__(self):
            self.passed_default = False

        @defaultevent
        async def on_default(self, default:bool):
            self.passed_default = default
        
    e = TestDefaultEvent()
    e.on_default.freeze()

    await e.on_default.send(True)
    assert e.passed_default == True

    await e.on_default.send(False)
    assert e.passed_default == False


@pytest.mark.asyncio
async def test_default_event_with_normal_event_override():

    class TestDefaultEvent:
        def __init__(self):
            self.passed_default = False

        @defaultevent
        async def on_default(self, default:bool) -> None:
            raise RuntimeError("Default should not have been ran and overwritten instead")
    
    e = TestDefaultEvent()
    
    @e.on_default
    async def on_default(default:bool):
        e.passed_default = default 
    
    e.on_default.freeze()

    await e.on_default.send(True)
    assert e.passed_default == True

    await e.on_default.send(False)
    assert e.passed_default == False

@pytest.mark.asyncio
async def test_default_event_with_default_event_override():

    class TestDefaultEvent:
        def __init__(self):
            self.passed_default = False

        @defaultevent
        async def on_default(self, default:bool) -> None:
            assert False, "Default should not have been ran and overwritten instead"

    e = TestDefaultEvent()
    
    @e.on_default.default
    async def on_default(default:bool):
        e.passed_default = default 
    
    e.on_default.freeze()
    await e.on_default.send(True)
    assert e.passed_default == True

    await e.on_default.send(False)
    assert e.passed_default == False

