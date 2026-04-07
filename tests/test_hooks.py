from aiocallback.hooks import Hook
from contextlib import asynccontextmanager

import pytest

class Owner:
    pass

@pytest.fixture
def hook() -> Hook[int]:
    return Hook(Owner())

@pytest.mark.anyio
async def test_hook(hook: Hook[int]):
    @asynccontextmanager
    async def hook_a(i: int):
        yield f"{i}"

    hook["a"] = hook_a
    hook.freeze()
    async with hook.send(1) as h:
        assert h["a"] == "1"

@pytest.mark.anyio
async def test_unfrozen_runtimeerror(hook: Hook[int]):
    async def hook_a(i: int):
        yield f"{i}"

    hook["a"] = hook_a
    with pytest.raises(RuntimeError, match="Cannot enter into non-frozen life-cycle."):
        async with hook.send(1) as h:
            pass
