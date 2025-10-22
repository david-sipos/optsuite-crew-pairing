"""
Convert the Airline Crew Pairing Problem to the Minimum Cost Exact Cover Problem.
"""

import numpy as np

from vqaopt.core.plugin import Reduction
from vqaopt.impl.problems import MCECProblem

from ..acp_problem import ACPProblem


class ACP2MCEC(Reduction):
    """
    Convert the Airline Crew Pairing Problem to the Minimum Cost Exact Cover Problem.
    """

    source = ACPProblem
    target = MCECProblem

    def reduce(
        self, problem_instance: ACPProblem, options: dict | None = None
    ) -> MCECProblem:
        assert isinstance(problem_instance, ACPProblem)
        pairing_contains_leg = np.zeros(
            (len(problem_instance.pairings), len(problem_instance.legs)),
            dtype=np.float64,
        )
        costs = np.zeros((len(problem_instance.pairings)), dtype=np.float64)

        for i, pairing in enumerate(problem_instance.pairings):
            for j, leg in enumerate(problem_instance.legs):
                if leg in pairing.legs_iterator:
                    pairing_contains_leg[i, j] = 1
            costs[i] = problem_instance.cost_model.cost(pairing)

        return MCECProblem(pairing_contains_leg.T, costs, forms=problem_instance.forms)
