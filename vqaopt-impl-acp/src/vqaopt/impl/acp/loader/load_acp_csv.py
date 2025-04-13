"""
Load the ACP problem from a CSV file.
"""

import typing
from datetime import datetime

from vqaopt.core.plugin import Field, ProblemLoader

from ..acp_problem import ACPProblem
from ..cost_model import ACPCostModel
from ..data_model import Leg, LegContainer, Pairing
from ..data_model.duty_generation import DutyGenerator
from ..data_model.pairing_generation import PairingGenerator
from ..rule import ACPDutyRule, ACPPairingRule
from ..utils import load_legs_from_file


class LoadACP_CSV(ProblemLoader[ACPProblem]):
    """
    Load flight legs from a CSV file and generate pairings for the ACP problem
    based on `cost_model`, `duty_rules` and `pairing_rules`.
    """

    cost_model: ACPCostModel = Field(
        title="Select cost model",
    )
    duty_rules: set[ACPDutyRule] = Field(
        title="Select duty rules",
    )
    pairing_rules: set[ACPPairingRule] = Field(
        title="Select pairing rules",
    )
    import_from: str | list[str] = Field(
        default="",
        title="Set data source",
    )

    @classmethod
    def get_name(cls) -> str:
        return "Load ACP CSV"

    @staticmethod
    def get_problem_type() -> type[ACPProblem]:
        return ACPProblem

    def load_problem(self) -> ACPProblem:

        legs = self.load_raw_data()

        daily_duties = DutyGenerator.generate_full_period(legs, self.duty_rules)
        pairings: list[Pairing] = PairingGenerator.generate_full_period(
            daily_duties, self.pairing_rules
        )
        return ACPProblem(legs=legs, pairings=pairings, cost_model=self.cost_model)

    def load_raw_data(self) -> LegContainer:
        """
        Parse the CSV file and return a container with the flight legs.
        """

        import_list = self.import_from
        if isinstance(self.import_from, str):
            import_list = [self.import_from]

        def process_row(row: typing.Sequence[str]) -> Leg:
            departure_airport: str = row[1].strip()
            departure_datetime: datetime = datetime.strptime(
                row[2].strip() + row[3].strip(), "%Y-%m-%d%H:%M"
            )
            arrival_airport: str = row[4].strip()
            arrival_datetime: datetime = datetime.strptime(
                row[5].strip() + row[6].strip(), "%Y-%m-%d%H:%M"
            )
            flight_designator: str = row[0].strip()
            is_dep_home_base = departure_airport.lower().startswith("base")
            return Leg(
                departure_airport,
                departure_datetime,
                arrival_airport,
                arrival_datetime,
                flight_designator,
                is_dep_home_base,
            )

        return LegContainer(
            leg
            for path in import_list
            for leg in load_legs_from_file(process_row, path)
        )

    def problem_count(self) -> int | None:
        return 1
