import asyncio
import sys

import pytest
import pytest_asyncio

if sys.version_info < (3, 14):
    @pytest.fixture(scope="module")
    def event_loop_policy():
        if sys.platform != "win32":
            import uvloop  # type:ignore
            return uvloop.EventLoopPolicy()
        else:
            import winloop  # type:ignore
            return winloop.EventLoopPolicy()

@pytest_asyncio.fixture(loop_scope="module")
async def current_loop():
    return asyncio.get_running_loop()

