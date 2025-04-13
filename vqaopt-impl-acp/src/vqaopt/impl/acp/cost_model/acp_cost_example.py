"""
An example cost model.
"""

from ..data_model.pairing import Pairing
from .cost_model import ACPCostModel


class ACPCostExample(ACPCostModel):

    @staticmethod
    def get_name() -> str:
        return "ACP Cost Example"

    def cost(self, pairing: Pairing) -> float:
        total_days = (
            1 + (pairing.end_datetime.date() - pairing.start_datetime.date()).days
        )
        hotel_stays = sum(
            1 if duty.arrival_airport == pairing.home_base else 0
            for duty in pairing.duties
        )

        overtime = sum(
            (
                max(
                    0,
                    (
                        leg.departure_datetime
                        - leg.departure_datetime.replace(hour=20, minute=0)
                    ).total_seconds(),
                )
                + max(
                    0,
                    (
                        leg.arrival_datetime.replace(hour=5, minute=0)
                        - leg.arrival_datetime
                    ).total_seconds(),
                )
            )
            / 3600
            for leg in pairing.legs_iterator
        )

        return total_days * 1000 + hotel_stays * 300 + overtime * 50
