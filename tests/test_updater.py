import pytest

from aiocallback.updater import Cache, Updater, UpdateSignal


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


class TestCache:
    def test_cache(self) -> None:
        cache: Cache[int] = Cache()
        cache.add(1)
        cache.add(2)
        cache.add(2)
        cache.add(3)
        assert cache.keys() == {1, 2, 3}

    def test_cache_ordering_mechnaism(self) -> None:
        cache: Cache[int] = Cache()
        cache.add(1)
        cache.add(2)
        cache.add(2)
        cache.add(3)
        cache.reset()
        # now add 4, 5, 6  these should be existant on the next movement made.
        cache.add(4)
        cache.add(5)
        cache.add(6)
        assert cache.keys() == {1, 2, 3, 4, 5, 6}
        # reset and remove 1, 2, 3 there should only be a 4, 5 and 6
        cache.reset()
        assert cache.keys() == {4, 5, 6}

    def test_disallowing_older_entries_even_with_double_reset(self) -> None:
        cache: Cache[int] = Cache()
        cache.add(1)
        cache.add(2)
        cache.add(2)
        cache.add(3)
        cache.reset()
        # There were no entires to update with so this reset is a dud.
        cache.reset()
        # now add 4, 5, 6  these should be existant on the next movement made.
        cache.add(4)
        cache.add(5)
        cache.add(6)
        assert cache.keys() == {1, 2, 3, 4, 5, 6}

    def test_clearing_the_cache(self) -> None:
        cache: Cache[int] = Cache()
        cache.add(1)
        cache.add(2)
        cache.add(2)
        cache.add(3)
        cache.clear()
        assert not cache.keys()
        cache.add(1)
        cache.add(2)
        cache.add(2)
        cache.add(3)
        assert cache.keys() == {1, 2, 3}


@pytest.mark.anyio
async def test_updatable_callbacks(
    updater: tuple[Updater[int], list[int]],
) -> None:
    listener, order = updater
    await listener.check(1)
    await listener.check(2)
    await listener.check(2)
    await listener.check(3)

    assert order == [1, 2, 3]


@pytest.mark.anyio
async def test_polling(updater: tuple[Updater[int], list[int]]) -> None:
    listener, order = updater
    await listener.poll([1, 2, 2, 2, 3])
    assert order == [1, 2, 3]


@pytest.mark.anyio
async def test_polling_async(updater: tuple[Updater[int], list[int]]) -> None:
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
