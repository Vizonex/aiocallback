import pytest

from aiocallback.updater import Updater, UpdateSignal


@pytest.fixture
def updater() -> tuple[Updater[int], list[int]]:
    order: list[int] = []

    async def on_update(i: int):
        order.append(i)

    listener: Updater[int] = Updater(on_update)
    return listener, order


class Owner:
    def __init__(self):
        self.order: list[int] = []
        self.on_update = UpdateSignal(self, self.on_update_cb)

    async def on_update_cb(self, i: int):
        pass


@pytest.mark.anyio
async def test_updatable_callbacks(updater: tuple[Updater[int], list[int]]):
    listener, order = updater
    await listener.check(1)
    await listener.check(2)
    await listener.check(2)
    await listener.check(3)

    assert order == [1, 2, 3]


@pytest.mark.anyio
async def test_polling(updater: tuple[Updater[int], list[int]]):
    listener, order = updater
    await listener.poll([1, 2, 2, 2, 3])
    assert order == [1, 2, 3]


@pytest.mark.anyio
async def test_polling_async(updater: tuple[Updater[int], list[int]]):
    listener, order = updater

    async def async_poll():
        for i in [1, 2, 2, 2, 3]:
            yield i

    await listener.poll(async_poll())
    assert order == [1, 2, 3]


@pytest.mark.anyio
class TestUpdateSignal:
    async def test_callbacks(self):
        owner = Owner()

        @owner.on_update
        async def __on_update(i: int):
            assert i in {1, 2, 3}
            owner.order.append(i)

        owner.on_update.freeze()
        await owner.on_update.update(1)
        await owner.on_update.update(2)
        await owner.on_update.update(3)
        assert owner.order == [1, 2, 3]

    async def test_callbacks_runtime_error(self):
        owner = Owner()

        @owner.on_update
        async def __on_update(i: int):
            assert i in {1, 2, 3}
            owner.order.append(i)

        with pytest.raises(
            RuntimeError, match="Cannot update non-frozen signal."
        ):
            await owner.on_update.update(1)

    async def test_polling_callbacks(self):
        owner = Owner()

        @owner.on_update
        async def __on_update(i: int):
            assert i in {1, 2, 3}
            owner.order.append(i)

        owner.on_update.freeze()
        await owner.on_update.poll([1, 2, 3])
        assert owner.order == [1, 2, 3]

    async def test_polling_callbacks_async(self):
        owner = Owner()

        @owner.on_update
        async def __on_update(i: int):
            assert i in {1, 2, 3}
            owner.order.append(i)

        owner.on_update.freeze()

        async def async_poll():
            for i in [1, 2, 2, 2, 3]:
                yield i

        await owner.on_update.poll(async_poll())
        assert owner.order == [1, 2, 3]

    async def test_polling_callbacks_sync(self):
        owner = Owner()

        @owner.on_update
        async def __on_update(i: int):
            assert i in {1, 2, 3}
            owner.order.append(i)

        owner.on_update.freeze()

        def poll():
            yield from [1, 2, 2, 2, 3]

        await owner.on_update.poll(poll())
        assert owner.order == [1, 2, 3]

    async def test_callbacks_poll_runtime_error(self):
        owner = Owner()

        @owner.on_update
        async def __on_update(i: int):
            assert i in {1, 2, 3}
            owner.order.append(i)

        with pytest.raises(
            RuntimeError, match="Cannot update non-frozen signal."
        ):
            await owner.on_update.poll([1])

    async def test_callbacks_notify_runtime_error(self):
        owner = Owner()

        @owner.on_update
        async def __on_update(i: int):
            assert i in {1, 2, 3}
            owner.order.append(i)

        with pytest.raises(
            RuntimeError, match="Cannot send non-frozen signal."
        ):
            await owner.on_update.notify({"i": 1})

    async def test_exception_raising(self):
        owner = Owner()

        class Bad(Exception):
            pass

        @owner.on_update
        async def __on_bad(i: int):
            raise Bad("this is bad")

        owner.on_update.freeze()

        with pytest.raises(Bad, match=r"this is bad"):
            await owner.on_update.update(1)
        # There should be nothing here...
        assert owner.order == []
