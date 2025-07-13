import asyncio
import platform
import sys

import pytest



# XXX: PyPy has problems right now so it's also ignored.
if platform.python_implementation() != "PyPy":
    # NOTE: I am working to pytest-asyncio in the future to workaround needing event-loop-policies

    if sys.version_info <= (3, 14):
        from asyncio import DefaultEventLoopPolicy

        uvloop = pytest.importorskip("winloop" if sys.platform == "win32" else "uvloop")
        
        @pytest.fixture(
            scope="session",
            params=(
                DefaultEventLoopPolicy(),
                uvloop.EventLoopPolicy(),
            ),
            ids=str,
        )
        def event_loop_policy(
            request: pytest.FixtureRequest,
        ) -> asyncio.AbstractEventLoopPolicy:
            return request.param
