"""
Pairing related dataclasses and functions
"""

from datetime import datetime
from typing import Iterable, Iterator
from uuid import UUID
from uuid import uuid4 as uuid

from .duty import Duty
from .leg import Leg


class Pairing:
    """
    Stores an entire pairing.

    Field
    ----------
    `id` : UUID
        The identifier of the pairing, generated automatically
    `duties` : list[Duty]
        A list of duties in the pairing
    `legs` : Iterator[Leg]
        An iterator of flight legs within the pairing,
        ordered by departure date
    `duty_legs` : Iterator[Leg]
        An iterator of non-ftr flight legs within the pairing
    `home_base` : str
        The home base of the pairing
    `start_datetime` : datetime
        The start datetime of the pairing
    `end_datetime` : datetime
        The end datetime of the pairing
    """

    id: UUID
    duties: list[Duty]
    legs: Iterator[Leg]
    duty_legs: Iterator[Leg]
    home_base: str
    start_datetime: datetime
    end_datetime: datetime

    def __init__(self, duties: Iterable[Duty]) -> None:
        """
        Initializes a pairing from an interable of duties

        Parameters
        ----------
        duties : Iterable[Duty]
            The duties in the pairing
        """

        self.id = uuid()
        self.duties = list(duties)
        self.home_base = self.duties[0].departure_airport
        self.start_datetime = self.duties[0].legs[0].departure_datetime
        self.end_datetime = self.duties[-1].legs[-1].arrival_datetime

    @property
    def legs_iterator(self) -> Iterator[Leg]:
        """
        Returns an iterator of all the legs in the pairing.
        """

        return (leg for duty in self.duties for leg in duty.legs)

    def __repr__(self) -> str:
        return f"Pairing with {len(self.duties)} duties"
