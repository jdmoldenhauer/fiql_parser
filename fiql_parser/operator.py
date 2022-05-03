# -*- coding: utf-8 -*-
"""
FIQL has two operators. ";" which is the logical ``AND`` and "," for the
logical ``OR`` where ``AND`` has a logical precedence which is higher than that
of ``OR``.

The ``operator`` module includes the code used for managing comparison operator
acceptance, precedence, and representation of the FIQL ``Operator``.

Attributes:
    OPERATOR_MAP (dict of tuple): Mappings of FIQL operators to common terms
        and their associated precedence.
"""
from __future__ import annotations

from typing import Any
from typing import Final
from typing import Literal

from .exceptions import FiqlObjectException


OPERATOR_MAP: Final = {
    ';': ('AND', 2),
    ',': ('OR', 1),
}


class Operator:
    """
    The comparison ``Operator`` is the representation of the FIQL comparison
    operator.

    Attributes:
        value (string): The FIQL operator.
    """

    def __init__(self, fiql_op_str: Literal[';', ',']) -> None:
        """Initialize instance of ``Operator``.

        Args:
            fiql_op_str (string): The FIQL operator (e.g., ";").

        Raises:
            FiqlObjectException: Invalid FIQL operator.
        """
        if fiql_op_str not in OPERATOR_MAP:
            raise FiqlObjectException(f"'{fiql_op_str}' is not a valid FIQL operator")
        self.value = fiql_op_str

    def to_python(self) -> str:
        """Deconstruct the ``Operator`` instance to a string.

        Returns:
            string: The deconstructed ``Operator``.
        """
        return OPERATOR_MAP[self.value][0]

    def __str__(self) -> str:
        """Represent the ``Operator`` instance as a string.

        Returns:
            string: The represented ``Operator``.
        """
        return self.value

    def __eq__(self, other: Any) -> bool:
        """Of equal precedence.

        Args:
            other (Operator): The ``Operator`` we are comparing precedence
                against.

        Returns:
            boolean: ``True`` if of equal precedence of ``other``.
        """
        if isinstance(other, Operator):
            return OPERATOR_MAP[self.value][1] == OPERATOR_MAP[other.value][1]

        return NotImplemented

    def __lt__(self, other: 'Operator') -> bool:
        """Of less than precedence.

        Args:
            other (Operator): The ``Operator`` we are comparing precedence
                against.

        Returns:
            boolean: ``True`` if of less than precedence of ``other``.
        """
        return OPERATOR_MAP[self.value][1] < OPERATOR_MAP[other.value][1]
