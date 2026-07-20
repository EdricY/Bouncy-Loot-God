from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, cast

from mods_base import ENGINE

if TYPE_CHECKING:
    from common import WillowGameEngine

__all__ = ["Time"]


class _Time:
    def __init__(self) -> None:
        self._delta_time: float = 0
        self._time: float = 0
        self._time_scale: float = 1
        self._unscaled_delta_time: float = 0

    @property
    def delta_time(self) -> float:
        """The time in seconds from the last frame to the current frame. Affected by timescale."""
        return self._delta_time

    @property
    def time(self) -> float:
        """The time in seconds at the beginning of the current frame."""
        return self._time

    @property
    def time_scale(self) -> float:
        """The scale at which the time is passing."""
        with contextlib.suppress(AttributeError, TypeError):
            self._time_scale = cast("WillowGameEngine", ENGINE).GetCurrentWorldInfo().TimeDilation
        return self._time_scale

    @time_scale.setter
    def time_scale(self, value: float) -> None:
        self._time_scale = value
        cast("WillowGameEngine", ENGINE).GetCurrentWorldInfo().TimeDilation = value

    @property
    def unscaled_delta_time(self) -> float:
        """The time in seconds from the last frame to the current frame, ignoring timescale."""
        return self._unscaled_delta_time


Time = _Time()
