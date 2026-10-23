import sys
from typing import ParamSpec, Self, TypeVar, Unpack

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

__all__ = ("_K", "_P", "_P2", "_T", "_V", "Self", "Unpack", "_Ts")
