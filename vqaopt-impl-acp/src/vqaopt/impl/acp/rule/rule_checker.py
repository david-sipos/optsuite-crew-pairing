"""
This module contains the rule checker for pairing and duty validation.
"""

import typing

from ..data_model import Duty, Leg
from .rule import ACPDutyRule, ACPPairingRule


def is_valid_duty(
    legs: typing.Sequence[Leg], duty_rules: typing.Sequence[ACPDutyRule]
) -> bool:
    """
    Validates a duty based on the rules passed during initialization.

    Parameters
    ----------
    `legs` : Sequence[Leg]
        The legs to validate.

    Returns
    ----------
    bool
        True if the duty is valid.
    """

    return all(map(lambda rule: rule.is_valid(legs), duty_rules))


def is_valid_pairing(
    duties: typing.Sequence[Duty], pairing_rules: typing.Sequence[ACPPairingRule]
) -> bool:
    """
    Validates a pairing based on the rules passed during initialization.

    Parameters
    ----------
    `duties` : Sequence[Duty]
        The duties to validate.

    Returns
    ----------
    bool
        True if the pairing is valid.
    """

    return all(map(lambda rule: rule.is_valid(duties), pairing_rules))
