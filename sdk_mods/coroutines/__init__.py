from mods_base import Library, build_mod

from .gametime import Time
from .loop import (
    PostRenderCoroutine,
    TickCoroutine,
    WaitCondition,
    WaitForSeconds,
    WaitUntil,
    WaitWhile,
    start_coroutine_post_render,
    start_coroutine_tick,
)

__all__ = [
    "PostRenderCoroutine",
    "TickCoroutine",
    "Time",
    "WaitCondition",
    "WaitForSeconds",
    "WaitUntil",
    "WaitWhile",
    "start_coroutine_post_render",
    "start_coroutine_tick",
]

__version__: str
__version_info__: tuple[int, ...]


mod = build_mod(cls=Library, hooks=[])
