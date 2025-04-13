"""
Duty related data models and functions
"""

from __future__ import annotations

import typing
from dataclasses import dataclass, field
from datetime import date
from functools import total_ordering
from uuid import UUID
from uuid import uuid4 as uuid

from sortedcontainers import SortedList

from .leg import Leg, LegContainer


@total_ordering
class Duty:
    """
    Duty period of one day

    Fields
    ----------
    id : UUID
        The identifier of the fdp, generated automatically
    day : Date
        The date of the day of the departure of the first leg in the fdp
    legs : LegContainer
        The sorted list of legs in the fdp
    num_duty_legs : int
        The number of on duty (non-ftr) legs
    departure_airport : str
        The code of the airport the first leg departs from
    arrival_airport : str
        The code of the airport the last leg arrives at
    """

    id: UUID
    day: date
    legs: LegContainer
    num_duty_legs: int
    departure_airport: str
    arrival_airport: str

    def __init__(self, legs: typing.Sequence[Leg]) -> None:
        self.id = uuid()
        self.legs = legs if isinstance(legs, LegContainer) else LegContainer(legs)
        self.starts_at_home_base = self.legs[0].is_dep_home_base
        self.day = self.legs[0].departure_datetime.date()
        self.departure_airport = self.legs[0].departure_airport
        self.arrival_airport = self.legs[-1].arrival_airport

    def __lt__(self, other: Duty) -> bool:
        return self.day < other.day

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Duty):
            return False

        return self.is_similar_to(other)

    def is_similar_to(self, other: Duty) -> bool:
        """
        Returns whether `other` has the same legs as this Duty.

        Parameters
        ----------
        `other` : Duty
            The Duty to compare to.
        """

        if not isinstance(other, Duty):
            return False

        if len(self.legs) != len(other.legs):
            return False
        for leg, other_leg in zip(self.legs, other.legs):
            if leg != other_leg:
                return False
        return True

    def __repr__(self) -> str:
        return f"Duty with {len(self.legs)} legs"


@dataclass(init=False, order=True)
class DailyDuties:
    """
    Stores a sorted list of the duty periods of a day.
    """

    day: date
    duties: SortedList = field(compare=False)
    num_duties: int = field(compare=False)

    def __init__(self, duties: typing.Sequence[Duty]) -> None:
        """
        Initilize a daily duties container from an iterable of duty periods.

        Parameters
        ----------
        `duties` : Iterable[Duty]
            The duty periods to store in the container,
            note that no checks are performed to ensure that all duties periods start
            on the same day
        """

        self.duties = SortedList(duties)
        self.num_duties = len(self.duties)
        self.day = self.duties[0].legs[0].departure_datetime.date()


class DutyContainer(SortedList):
    """
    Sorted list of the duty periods grouped by days.
    """

    num_duties: int

    def __init__(self, daily_duties: typing.Iterable[DailyDuties]):
        """
        Initilize a sorted list of daily duty periods containers
        from an iterable of daily duty periods.

        Parameters
        ----------
        `daily_duties` : Iterable[DailyDuties]
            The duties grouped into containers for each day
        """

        super().__init__(daily_duties)
        self.num_duties = sum((daily_duty.num_duties for daily_duty in daily_duties))
