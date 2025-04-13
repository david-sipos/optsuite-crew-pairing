"""
Cost model plugin base class.
"""

from abc import abstractmethod

from vqaopt.core.plugin import Plugin

from ..data_model import Pairing


class ACPCostModel(Plugin):

    @abstractmethod
    def cost(self, pairing: Pairing) -> float:
        """
        Returns the cost of a pairing

        Parameters
        ----------
        pairing : Pairing
            The pairing to calculate the cost of

        Returns
        ----------
        float
            The cost of the pairing
        """
