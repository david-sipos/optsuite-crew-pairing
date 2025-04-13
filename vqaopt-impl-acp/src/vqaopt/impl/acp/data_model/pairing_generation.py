from typing import Sequence

from ..data_model import Duty, DutyContainer, Pairing
from ..rule import ACPPairingRule, is_valid_pairing


class PairingGenerator:
    """
    Pairing generator
    """

    @staticmethod
    def generate_full_period(
        duty_container: DutyContainer,
        pairing_rules: Sequence[ACPPairingRule],
    ) -> list[Pairing]:
        """
        Generates valid pairings from multiple days of duty periods.

        Parameters
        ----------
        duty_container : DutyContainer
            The ordered list of daily duties to build pairings from
        """

        pairings: list[Pairing] = []
        to_expand: list[tuple[int, list[Duty]]] = [
            (day, [duty])
            for day, daily_duties in enumerate(duty_container)
            for duty in daily_duties.duties
            if is_valid_pairing([duty], pairing_rules)
        ]
        for day, duties in to_expand:
            if (
                duties[0].departure_airport == duties[-1].arrival_airport
                and duties[0].starts_at_home_base
            ):
                pairings.append(Pairing(duties))

        while len(to_expand) > 0:
            day, duties = to_expand.pop()
            for idx, daily_duties in enumerate(duty_container[day + 1 :]):
                for duty in daily_duties.duties:
                    if duties[-1].arrival_airport == duty.departure_airport:
                        if is_valid_pairing([*duties, duty], pairing_rules):
                            to_expand.append((day + idx + 1, [*duties, duty]))
                        if (
                            duties[0].departure_airport == duty.arrival_airport
                            and duties[0].starts_at_home_base
                        ):
                            pairings.append(Pairing([*duties, duty]))

        return pairings
