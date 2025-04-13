"""
This module contains the rules for pairing and duty validation.
"""

import itertools
import typing
from datetime import timedelta

from vqaopt.core.plugin import Field

from ..data_model import Duty, Leg
from .rule import ACPDutyRule, ACPPairingRule


class MaxFlights(ACPDutyRule):

    threshold: int = Field(
        default=4,
        title="Set maximum number of flights",
        ge=1,
    )

    @staticmethod
    def get_name() -> str:
        return "Max Flights"

    def is_valid(self, to_validate: typing.Sequence[Leg]) -> bool:
        return len(to_validate) <= self.threshold


class MinConnect(ACPDutyRule):
    threshold: int = Field(
        default=30,
        title="Set minimum connection time in minutes",
        ge=0,
    )

    @staticmethod
    def get_name() -> str:
        return "Min Connect"

    def is_valid(self, to_validate: typing.Sequence[Leg]) -> bool:
        for leg, next_leg in itertools.pairwise(to_validate):
            connection_time = next_leg.departure_datetime - leg.arrival_datetime
            if connection_time < timedelta(minutes=self.threshold):
                return False
        return True


class MaxDurationDutyTime(ACPDutyRule):

    threshold: int = Field(
        default=12,
        title="Set maximum duration of a duty in hours",
        ge=1,
    )

    @staticmethod
    def get_name() -> str:
        return "Max Duration Duty Time"

    def is_valid(self, to_validate: typing.Sequence[Leg]) -> bool:
        return (
            to_validate[-1].arrival_datetime - to_validate[0].departure_datetime
        ) <= timedelta(hours=self.threshold)


class MaxDuties(ACPPairingRule):

    threshold: int = Field(
        default=5,
        title="Set maximum number of duties",
        ge=1,
    )

    @staticmethod
    def get_name() -> str:
        return "Max Duties"

    def is_valid(self, to_validate: typing.Sequence[Duty]) -> bool:
        return len(to_validate) <= self.threshold


class MinRest(ACPPairingRule):

    threshold: float = Field(
        default=9.5,
        title="Set minimum hours to rest",
        ge=0.0,
    )

    @staticmethod
    def get_name() -> str:
        return "Min Rest"

    def is_valid(self, to_validate: typing.Sequence[Duty]) -> bool:
        for duty, next_duty in itertools.pairwise(to_validate):
            last_leg: Leg = duty.legs[-1]
            first_leg_next_duty: Leg = next_duty.legs[0]
            rest = first_leg_next_duty.departure_datetime - last_leg.arrival_datetime
            if rest < timedelta(hours=self.threshold):
                return False
        return True
class MaxPairingDuration(ACPPairingRule):

    threshold: int = Field(
        default=4,
        title="Set maximum pairing duration in days",
        ge=1,
    )

    @staticmethod
    def get_name() -> str:
        return "Max Pairing Duration"

    def is_valid(self, to_validate: typing.Sequence[Duty]) -> bool:
        return (to_validate[-1].day - to_validate[0].day).days <= self.threshold
