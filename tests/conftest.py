import asyncio
import sys
import platform
import pytest
import pytest_asyncio

uvloop = pytest.importorskip("winloop" if sys.platform == "win32" else "uvloop")


# XXX: PyPy has problems right now so it's also ignored.
if platform.python_implementation() != "PyPy":
    # NOTE: I am working to pytest-asyncio in the future to workaround needing event-loop-policies

    if sys.version_info >= (3, 14):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from asyncio import DefaultEventLoopPolicy
    else:
        from asyncio import DefaultEventLoopPolicy

    @pytest.fixture(
        scope="session",
        params=(
            DefaultEventLoopPolicy(),
            uvloop.EventLoopPolicy(),
        ),
        ids=str
    )
    def event_loop_policy(request:pytest.FixtureRequest) -> asyncio.AbstractEventLoopPolicy:
        return request.param
