"""
Introduces data models for working with flight legs.
"""

from __future__ import annotations

import typing
from dataclasses import dataclass, field
from datetime import datetime
from functools import total_ordering

from sortedcontainers import SortedList


@dataclass()
@total_ordering
class Leg:
    """
    A flight leg.

    Fields
    ----------
    `departure_airport` : str
        The code of the departure airport
    `departure_datetime` : datetime
        The datetime of departure
    `arrival_airport` : str
        The code of the arrival airport
    `arrival_datetime` : datetime
        The datetime of arrival
    `flight_designator` : str
        The flight designator of the flight
    `is_dep_home_base` : bool
        Whether the departure airport is a home base
    """

    departure_airport: str
    departure_datetime: datetime
    arrival_airport: str = field(compare=False)
    arrival_datetime: datetime = field(compare=False)
    flight_designator: str
    is_dep_home_base: bool = field(compare=False)

    def __lt__(self, other: Leg) -> bool:
        if self.departure_datetime == other.departure_datetime:
            return self.departure_airport < other.departure_airport
        return self.departure_datetime < other.departure_datetime

    def __repr__(self) -> str:
        return f'{self.departure_datetime.strftime("%d%m%Y-%H%M")} {self.flight_designator} {self.departure_airport}'


class LegContainer(SortedList):
    """
    A sorted list of flight legs.
    """

    def __init__(self, legs: typing.Iterable[Leg]) -> None:
        """
        Initialize a sorted list of flight legs from an iterable of flight legs.

        Parameters
        ----------
        `legs` : Iterable[Leg]
            The flight legs to store in the sorted list
        """

        super().__init__(legs)

    def split_by_day(self) -> list[LegContainer]:
        """
        Returns a list of LegContainers, each containing Legs of a single day.

        Returns
        ----------
        List[LegContainer]
            The list of LegContainers, each containing the legs of one day.
        """

        if self[0].departure_datetime.date() == self[-1].departure_datetime.date():
            return [self]

        daily_legs = []
        date = self[0].departure_datetime.date()
        from_index = 0
        for i, leg in enumerate(self):
            curr_date = leg.departure_datetime.date()
            if curr_date != date:
                daily_legs.append(LegContainer(self.islice(from_index, i)))
                date = curr_date
                from_index = i
        daily_legs.append(LegContainer(self.islice(from_index)))

        return daily_legs
