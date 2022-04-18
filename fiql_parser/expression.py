# -*- coding: utf-8 -*-
"""
It would be very difficult to build a FIQL ``Expressions`` without taking into
account the ``Expressions`` part of it.

The ``expression`` module includes the code used for ensuring that any FIQL
``Expression`` created with this package is a valid FIQL ``Expression``.
"""

from .exceptions import FiqlObjectException
from .operator import Operator


class BaseExpression:
    """
    Both ``Constraint`` and ``Expression`` classes extend the
    ``BaseExpression`` class. A FIQL ``Constraint`` is a simple FIQL
    ``Expression``. As such, they share certain attributes.

    Note:

        The parent of any child of ``BaseExpression`` is always an
        ``Expression``. This is a bit contrary to what might be expected as an
        ``Expression`` itself is a child class of ``BaseExpression``.

        This quark is a side effect of the definition of the FIQL
        ``Constraint``. A FIQL ``Constraint`` can not be contained within
        another FIQL ``Constraint`` as a sub-expression. Both a FIQL
        ``Constraint`` and FIQL ``Expression`` can only be sub-expressions of
        an actual FIQL ``Expression``.

    Attributes:
        parent (Expression): The ``Expression`` which contains this object.
    """

    def __init__(self):
        """Initialize instance of ``BaseExpression``."""
        self.parent = None

    def set_parent(self, parent):
        """Set parent ``Expression`` for this object.

        Args:
            parent (Expression): The ``Expression`` which contains this object.

        Raises:
            FiqlObjectException: Parent must be of type ``Expression``.
        """
        if not isinstance(parent, Expression):
            raise FiqlObjectException('Parent must be of %s not %s' % (Expression, type(parent)))
        self.parent = parent

    def get_parent(self):
        """Get the parent ``Expression`` for this object.

        Returns:
            Expression: The ``Expression`` which contains this object.

        Raises:
            FiqlObjectException: Parent is ``None``.
        """
        if not isinstance(self.parent, Expression):
            raise FiqlObjectException(
                'Parent must be of %s not %s' % (Expression, type(self.parent))
            )
        return self.parent


class Expression(BaseExpression):

    """
    The ``Expression`` is the largest logical unit of a FIQL ``Expression``. It
    must, like the ``Constraint`` evaluate to ``True`` or ``False``. The
    ``Expression`` can both contain and be contained by an ``Expression``. It,
    unlike the ``Operator`` and ``Constraint``, MUST contain specific
    attributes in order to be valid.

    This class contains the bulk of the logic to ensure that an ``Expression``
    generated by this code is a valid FIQL ``Expression``.

    Note:
        This ``Expression`` class uses a single ``Operator`` to join multiple
        ``Constraints``. This format has the advantage of working cleanly with
        many ORMs and being far more easily converted to the more string
        friendly format of ``Constraint``, ``Operator``, ``Constraint``, etc.
        than the more string friendly format can be converted to the other.

    Attributes:
        elements (list): List of ``Constraint`` and ``Expression`` elements in
            this ``Expression``.
        operator (Operator): The ``Operator`` which relates the elements in
            this ``Expression``.
    """

    def __init__(self):
        """Initialize instance of ``Expression``."""
        super(Expression, self).__init__()
        self.elements = []
        self.operator = None
        # Keep track of which nested fragment we are in.
        self._working_fragment = self
        # Keep track of what was last added.
        self._last_element = None

    def has_constraint(self):
        """Return whether or not the working ``Expression`` has any
        ``Constraints``.

        Returns:
            integer: Number of logical elements within this ``Expression``.
        """
        return len(self.elements)

    def add_operator(self, operator):
        """Add an ``Operator`` to the ``Expression``.

        The ``Operator`` may result in a new ``Expression`` if an ``Operator``
        already exists and is of a different precedence.

        There are three possibilities when adding an ``Operator`` to an
        ``Expression`` depending on whether or not an ``Operator`` already
        exists:

          - No ``Operator`` on the working ``Expression``; Simply set the
            ``Operator`` and return ``self``.
          - ``Operator`` already exists and is higher in precedence; The
            ``Operator`` and last ``Constraint`` belong in a sub-expression of
            the working ``Expression``.
          - ``Operator`` already exists and is lower in precedence; The
            ``Operator`` belongs to the parent of the working ``Expression``
            whether one currently exists or not. To remain in the context of
            the top ``Expression``, this method will return the parent here
            rather than ``self``.

        Args:
            operator (Operator): What we are adding.

        Returns:
            Expression: ``self`` or related ``Expression``.

        Raises:
            FiqlObjectExpression: Operator is not a valid ``Operator``.
        """
        if not isinstance(operator, Operator):
            raise FiqlObjectException('%s is not a valid element type' % (operator.__class__))

        if not self._working_fragment.operator:
            self._working_fragment.operator = operator
        elif operator > self._working_fragment.operator:
            last_constraint = self._working_fragment.elements.pop()
            self._working_fragment = self._working_fragment.create_nested_expression()
            self._working_fragment.add_element(last_constraint)
            self._working_fragment.add_operator(operator)
        elif operator < self._working_fragment.operator:
            if self._working_fragment.parent:
                return self._working_fragment.parent.add_operator(operator)
            else:
                return Expression().add_element(self._working_fragment).add_operator(operator)
        return self

    def add_element(self, element):
        """Add an element of type ``Operator``, ``Constraint``, or
        ``Expression`` to the ``Expression``.

        Args:
            element: ``Constraint``, ``Expression``, or ``Operator``.

        Returns:
            Expression: ``self``

        Raises:
            FiqlObjectException: Element is not a valid type.
        """
        if isinstance(element, BaseExpression):
            element.set_parent(self._working_fragment)
            self._working_fragment.elements.append(element)
            return self
        else:
            return self.add_operator(element)

    def create_nested_expression(self):
        """Create a nested ``Expression``, add it as an element to this
        ``Expression``, and return it.

        Returns:
            Expression: The newly created nested ``Expression``.
        """
        sub = Expression()
        self.add_element(sub)
        return sub

    def op_and(self, *elements):
        """Update the ``Expression`` by joining the specified additional
        ``elements`` using an "AND" ``Operator``

        Args:
            *elements (BaseExpression): The ``Expression`` and/or
                ``Constraint`` elements which the "AND" ``Operator`` applies
                to.

        Returns:
            Expression: ``self`` or related ``Expression``.
        """
        expression = self.add_operator(Operator(';'))
        for element in elements:
            expression.add_element(element)
        return expression

    def op_or(self, *elements):
        """Update the ``Expression`` by joining the specified additional
        ``elements`` using an "OR" ``Operator``

        Args:
            *elements (BaseExpression): The ``Expression`` and/or
                ``Constraint`` elements which the "OR" ``Operator`` applies
                to.

        Returns:
            Expression: ``self`` or related ``Expression``.
        """
        expression = self.add_operator(Operator(','))
        for element in elements:
            expression.add_element(element)
        return expression

    def to_python(self):
        """Deconstruct the ``Expression`` instance to a list or tuple
        (If ``Expression`` contains only one ``Constraint``).

        Returns:
            list or tuple: The deconstructed ``Expression``.
        """
        if len(self.elements) == 0:
            return None
        if len(self.elements) == 1:
            return self.elements[0].to_python()
        operator = self.operator or Operator(';')
        return [operator.to_python()] + [elem.to_python() for elem in self.elements]

    def __str__(self):
        """Represent the ``Expression`` instance as a string.

        Returns:
            string: The represented ``Expression``.
        """
        operator = self.operator or Operator(';')
        elements_str = str(operator).join(['{0}'.format(elem) for elem in self.elements])
        if self.parent:
            parent_operator = self.parent.operator or Operator(';')
            if parent_operator > operator:
                return '(' + elements_str + ')'
        return elements_str
