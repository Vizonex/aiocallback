import asyncio
import sys
import platform
import pytest
import pytest_asyncio


# XXX: PyPy has problems right now so it's also ignored.
if platform.python_implementation() != "PyPy":
    @pytest.fixture(scope="module")
    def event_loop():
        if sys.platform != "win32":
            try:
                import uvloop  # type:ignore
                return uvloop.new_event_loop()
            except ModuleNotFoundError: 
                # fallback
                return asyncio.new_event_loop()
        else:
            import winloop  # type:ignore
            return winloop.new_event_loop()
        


@pytest_asyncio.fixture(loop_scope="module")
async def current_loop():
    return asyncio.get_running_loop()
