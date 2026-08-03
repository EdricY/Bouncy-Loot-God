from __future__ import annotations

from collections.abc import Callable, Generator
from dataclasses import dataclass
from time import time
from typing import TYPE_CHECKING, Any, TypeVar, cast

import unrealsdk
from unrealsdk.hooks import Type, add_hook
from unrealsdk.unreal import WeakPointer
from mods_base import Game

from coroutines.gametime import Time

if TYPE_CHECKING:
    from common import Canvas
__all__ = [
    "PostRenderCoroutine",
    "TickCoroutine",
    "WaitCondition",
    "WaitForSeconds",
    "WaitUntil",
    "WaitWhile",
    "start_coroutine_post_render",
    "start_coroutine_tick",
]

T = TypeVar("T")
class WaitForSeconds:
    """Wait for the specified amount of time."""

    def __init__(self, seconds: float, unscaled: bool = False) -> None:
        self._seconds: float = seconds
        self._unscaled: bool = unscaled

    def __call__(self) -> bool:
        """Return True if the time has not passed, False if it has."""
        self._seconds -= Time.unscaled_delta_time if self._unscaled else Time.delta_time
        return self._seconds > 0


class WaitWhile:
    """Wait until the condition is false."""

    def __init__(self, condition: Callable[[], bool]) -> None:
        self._condition: Callable[[], bool] = condition

    def __call__(self) -> bool:
        """Return True if the condition is still true, False if it is false."""
        return self._condition()


class WaitUntil:
    """Wait until the condition is true."""

    def __init__(self, condition: Callable[[], bool]) -> None:
        self._condition: Callable[[], bool] = condition

    def __call__(self) -> bool:
        """Return True if the condition is still false, False if it is true."""
        return not self._condition()


WaitCondition = WaitForSeconds | WaitWhile | WaitUntil | None

TickCoroutine = Generator[WaitCondition]
PostRenderCoroutine = Generator[WaitCondition, WeakPointer["Canvas"]]


@dataclass
class CoroutineData[T: TickCoroutine | PostRenderCoroutine]:
    __slots__ = ("coroutine", "wait")
    coroutine: T
    wait: WaitCondition


_TICK: list[CoroutineData[TickCoroutine]] = []
_POST_RENDER: list[CoroutineData[PostRenderCoroutine]] = []


def start_coroutine_tick(coroutine: TickCoroutine) -> None:
    """Start a coroutine that will be called every frame.
    Example:
        >>> def coroutine_once_a_second() -> TickCoroutine:
        >>>     while True:
        >>>         print("Tick")
        >>>         yield WaitForSeconds(1)
        >>>         if not mod_instance.IsEnabled:
        >>>             printg("Disable")
        >>>             return None  # Break out of the coroutine
        >>> start_coroutine_tick(coroutine_once_a_second())  # Start the coroutine

    """
    try:
        result = next(coroutine)  # Start the coroutine
        _TICK.append(CoroutineData(coroutine, result))
    except StopIteration:
        unrealsdk.logging.dev_warning("[coroutines] Coroutine returned before it started.")


def start_coroutine_post_render(coroutine: PostRenderCoroutine) -> None:
    """Start a coroutine that will be called every frame after the game has rendered.
    Example:
        >>> def coroutine_draw_x() -> PostRenderCoroutine:
        >>>     while True:
        >>>         # We need to yield our Wait condition before receiving the canvas to make sure
        >>>         # that the canvas object is not garbage collected while waiting.
        >>>         yield WaitUntil(lambda: unrealsdk.GetEngine().GamePlayers[0].Actor.GetHUDMovie() is not None)
        >>>         canvas = yield
        >>>         canvas.SetPos(int(canvas.SizeX / 2), int(canvas.SizeY / 2), 0)
        >>>         canvas.SetDrawColorStruct((0, 255, 0, 255))
        >>>         canvas.DrawText("X", False, 1, 1, ())
        >>>         if not mod_instance.IsEnabled:
        >>>             print("Disable")
        >>>             return None  # Break out of the coroutine
        >>> start_coroutine_post_render(coroutine_draw_x())  # Start the coroutine
    """
    try:
        result = next(coroutine)  # Start the coroutine
        _POST_RENDER.append(CoroutineData(coroutine, result))
    except StopIteration:
        unrealsdk.logging.dev_warning("[coroutines] Coroutine returned before it started.")


def _tick(
    _obj: unrealsdk.unreal.UObject,
    args: unrealsdk.unreal.WrappedStruct,
    _ret: Any,
    _func: unrealsdk.unreal.BoundFunction,
) -> None:
    Time._unscaled_delta_time = args.DeltaTime
    Time._delta_time = Time.unscaled_delta_time * Time.time_scale
    Time._time = time()
    # We need to iterate over a copy, as we want to remove a coroutine if it returns None
    for t in _TICK.copy():
        # Simply call the coroutine if we have no wait condition
        if t.wait is None:
            try:
                t.wait = t.coroutine.send(None)
            except StopIteration:  # The coroutine has finished
                _TICK.remove(t)
            continue
        # If we have a wait condition we need to check if it is still true
        if t.wait():
            continue
        try:
            # The wait condition returned false, so we can continue the coroutine
            t.wait = t.coroutine.send(None)
        except StopIteration:  # The coroutine has finished
            _TICK.remove(t)


def _post_render(
    _obj: unrealsdk.unreal.UObject,
    args: unrealsdk.unreal.WrappedStruct,
    _ret: Any,
    _func: unrealsdk.unreal.BoundFunction,
) -> None:
    # We want to make sure that the canvas object is not garbage collected while waiting
    # That is why we need to yield the wait condition before receiving the canvas
    # So the order of operation should be:
    #   1. Yield the wait condition
    #   2. Receive the canvas
    #   3. Run your code that relies on the canvas
    #   4. Repeat

    # Before the first call of next or send our coroutines are already primed
    # So they are on the yield Wait Condition state
    canvas = WeakPointer(cast("Canvas", args.Canvas))
    for t in _POST_RENDER.copy():
        # First check for any wait conditions
        if t.wait is not None and t.wait():
            continue

        # If we have no wait condition or the wait condition returned false
        # We can continue the coroutine
        try:
            # Get the next wait condition
            t.wait = next(t.coroutine)
            t.wait = cast(PostRenderCoroutine, t.coroutine).send(canvas)
        except StopIteration:  # The coroutine has finished
            _POST_RENDER.remove(t)


add_hook(
    "Engine.Interaction:PostRender",
    Type.PRE,
    "coroutines_post_render",
    _post_render,
)

if Game.get_tree() == Game.Willow1:
    add_hook(
        "Engine.GameViewportClient:Tick",
        Type.POST_UNCONDITIONAL,
        "coroutines_tick_frame",
        _tick,
    )
else:
    add_hook(
        "WillowGame.WillowGameViewportClient:Tick",
        Type.POST_UNCONDITIONAL,
        "coroutines_tick_frame",
        _tick,
    )