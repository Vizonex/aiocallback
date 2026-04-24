import pytest

from aiocallback.signals import ParentSignal


class Owner:
    def __repr__(self) -> str:
        return "<Owner 0xdead>"

    async def event(self, a: int, b: str | None = None) -> None:
        pass

    def __init__(self):
        # Creates ParentSignal[(a: int, b: str | None = None)]
        self.on_event = ParentSignal(self, self.event)


@pytest.fixture
def owner() -> Owner:
    return Owner()


@pytest.fixture
def wrapped_owner(owner: Owner) -> Owner:

    # Know that writing a full signature is not required it's
    # just good parctice.
    @owner.on_event
    async def on_event_1(a: int) -> None:
        assert a == 1

    async def on_event_2(b: str | None) -> None:
        assert b is None or b == "b"

    # Just another way to write this all
    # mostly is just here for testing
    owner.on_event.append(on_event_2)

    @owner.on_event
    async def on_event_3(a: int, b: str | None):
        await on_event_1(a)
        await on_event_2(b)

    @owner.on_event
    async def on_event_4(a: int, b: str | None):
        assert a == 1
        assert b is None or b == "b"

    # see if a function was registered.
    assert owner.on_event[0] == on_event_1

    return owner


@pytest.fixture
def wrapped_owner_frozen(wrapped_owner: Owner) -> Owner:
    wrapped_owner.on_event.freeze()
    return wrapped_owner


@pytest.mark.anyio
async def test_send(wrapped_owner_frozen: Owner) -> None:
    owner = wrapped_owner_frozen
    await owner.on_event.send(1, "b")
    await owner.on_event.send(a=1, b="b")
    await owner.on_event.send(1, b="b")
    await owner.on_event.send(1)


@pytest.mark.anyio
async def test_unfrozen(wrapped_owner: Owner) -> None:
    with pytest.raises(
        TypeError, match="Can't make callbacks from non-frozen siganl."
    ):
        for _ in wrapped_owner.on_event.signals:
            pass  # noop

    with pytest.raises(RuntimeError, match="Cannot send non-frozen signal."):
        await wrapped_owner.on_event.send(1, None)


def test_naming(wrapped_owner: Owner):
    assert wrapped_owner.on_event.name == "event"


def test_args(wrapped_owner: Owner):
    assert wrapped_owner.on_event.args == ("a",)


def test_kwargs(wrapped_owner: Owner):
    assert wrapped_owner.on_event.kwargs == ("b",)


@pytest.mark.anyio
async def test_sending_packed(wrapped_owner_frozen: Owner) -> None:
    await wrapped_owner_frozen.on_event.send_packed({"a": 1, "b": "b"})
    await wrapped_owner_frozen.on_event.send_packed({"a": 1, "b": None})


@pytest.mark.anyio
async def test_sending_packed_error(wrapped_owner: Owner) -> None:
    with pytest.raises(RuntimeError, match="Cannot send non-frozen signal."):
        await wrapped_owner.on_event.send_packed({"a": 1, "b": None})


def test_installation(wrapped_owner: Owner) -> None:
    assert {"a": 1, "b": None} == wrapped_owner.on_event.install(a=1)
