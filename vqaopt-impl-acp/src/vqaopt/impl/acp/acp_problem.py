import typing
from dataclasses import dataclass

from vqaopt.core.problem import Problem

from .cost_model import ACPCostModel
from .data_model import LegContainer, Pairing


@dataclass
class ACPProblem(Problem):
    legs: LegContainer
    pairings: list[Pairing]
    cost_model: ACPCostModel

    @staticmethod
    def get_name() -> str:
        return "acp"

    def cost_of_solution(self, solution: typing.Iterable[Pairing]) -> float:
        return sum(self.cost_model.cost(p) for p in solution)

    def pairings_from_bitstring(
        self, bitstring: typing.Iterable | int
    ) -> typing.Iterable[Pairing]:
        if isinstance(bitstring, int):
            bitstring = bin(bitstring)[2:]
            bitstring = (len(self.pairings) - len(bitstring)) * "0" + bitstring
        return (
            self.pairings[len(self.pairings) - 1 - i]
            for i, b in enumerate(bitstring)
            if int(b)
        )

    def cost_of_bitstring(self, bitstring: typing.Iterable | int) -> float:
        return sum(
            self.cost_model.cost(p) for p in self.pairings_from_bitstring(bitstring)
        )

    def get_instance_size(self) -> int:
        return len(self.pairings)
