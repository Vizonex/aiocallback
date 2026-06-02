import sys
from typing import ParamSpec, TypeVar

if sys.version_info >= (3, 11):
    from typing import Self, Unpack  # pragma: no cover - version differences
else:
    from typing_extensions import Self, Unpack

if sys.version_info >= (3, 13):
    from typing import TypeVarTuple  # pragma: no cover - version differences
else:
    from typing_extensions import TypeVarTuple


_Ts = TypeVarTuple("_Ts", default=Unpack[tuple[()]])
_T = TypeVar("_T")
_P = ParamSpec("_P")
_P2 = ParamSpec("_P2")
_K = TypeVar("_K")
_V = TypeVar("_V")

__all__ = ("_K", "_Ts", "_T", "_P", "_P2", "_V", "Unpack", "Self")
