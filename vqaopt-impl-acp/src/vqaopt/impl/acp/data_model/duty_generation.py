from typing import Sequence

from ..rule import ACPDutyRule, is_valid_duty
from .duty import DailyDuties, Duty, DutyContainer
from .leg import Leg, LegContainer


class DutyGenerator:
    """
    Generates duty periods
    """

    @staticmethod
    def generate(
        leg_container: LegContainer,
        duty_rules: Sequence[ACPDutyRule],
    ) -> DailyDuties:
        """
        Generates daily duty periods from a leg container.

        Parameters
        ----------
        `leg_container` : LegContainer
            A LegContainer storing legs of a single day.

        Returns
        ----------
        DailyDuties
            The possible duties of the day.
        """

        assert (
            leg_container[0].departure_datetime.date()
            == leg_container[-1].departure_datetime.date()
        ), "leg_container should only contain legs of a single day"

        to_expand: list[list[Leg]] = [
            [leg] for leg in leg_container if is_valid_duty([leg], duty_rules)
        ]
        duties: list[Duty] = [Duty(legs) for legs in to_expand]

        while len(to_expand) > 0:
            exp = to_expand.pop()
            last_leg = exp[-1]
            for leg in leg_container:
                if last_leg.arrival_airport == leg.departure_airport:
                    if last_leg.arrival_datetime < leg.departure_datetime:
                        if is_valid_duty([*exp, leg], duty_rules):
                            duty = Duty([*exp, leg])
                            duties.append(duty)
                            to_expand.append([*exp, leg])

        dailyDuties = DailyDuties(duties)

        return DailyDuties(duties)

    @staticmethod
    def generate_full_period(
        leg_container: LegContainer,
        duty_rules: Sequence[ACPDutyRule],
    ) -> DutyContainer:
        """
        Generates duty periods for multiple days

        Parameters
        ----------
        `leg_container`: LegContainer
            The LegContainer storing legs of multiple days.

        Returns
        ----------
        DutyContainer
            Sorted list of daily duties.
        """
        return DutyContainer(
            DutyGenerator.generate(daily_container, duty_rules)
            for daily_container in leg_container.split_by_day()
        )
