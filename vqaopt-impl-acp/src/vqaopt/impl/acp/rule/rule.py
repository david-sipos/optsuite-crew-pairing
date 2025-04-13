"""
Rule plugin base classes.
"""

from __future__ import annotations

import typing
from abc import abstractmethod

from vqaopt.core.plugin import Plugin

from ..data_model import Duty, Leg

T = typing.TypeVar("T")


class ACPRule(Plugin, typing.Generic[T]):

    @abstractmethod
    def is_valid(self, to_validate: T) -> bool:
        pass


class ACPDutyRule(ACPRule[typing.Sequence[Leg]]):
    pass


class ACPPairingRule(ACPRule[typing.Sequence[Duty]]):
    pass
