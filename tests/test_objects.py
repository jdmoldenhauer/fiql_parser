# -*- coding: utf-8 -*-
"""
Tests against the classes representing FIQL query objects.
"""
import pytest

from fiql_parser import Constraint
from fiql_parser import Expression
from fiql_parser import FiqlObjectException
from fiql_parser import Operator


def test_operator_init():
    with pytest.raises(FiqlObjectException, match="'i' is not a valid FIQL operator"):
        Operator('i')


def test_operator_precedence():
    operator_and = Operator(';')
    operator_or = Operator(',')

    assert operator_and == Operator(';')
    assert operator_or == Operator(',')
    assert operator_and != operator_or
    assert operator_and > operator_or
    assert operator_or < operator_and


def test_constraint_init_with_defaults():
    constraint = Constraint('foo')

    assert 'foo' == constraint.selector
    assert constraint.comparison is None
    assert constraint.argument is None
    assert 'foo' == str(constraint)


def test_constraint_init():
    constraint = Constraint('foo', '==', 'bar')

    assert 'foo' == constraint.selector
    assert '==' == constraint.comparison
    assert 'bar' == constraint.argument
    assert 'foo==bar' == str(constraint)


def test_constraint_init_invalid_comparison():
    with pytest.raises(FiqlObjectException, match="'=gt' is not a valid FIQL comparison"):
        Constraint('foo', '=gt', 'bar')


def test_constraint_set_parent():
    constraint = Constraint('foo')
    expression = Expression()

    constraint.set_parent(expression)

    assert expression == constraint.parent


def test_constraint_set_parent_invalid_parent():
    with pytest.raises(
        FiqlObjectException,
        match=(
            "Parent must be of <class 'fiql_parser.expression.Expression'>"
            " not <class 'fiql_parser.constraint.Constraint'>"
        ),
    ):
        Constraint('foo').set_parent(Constraint('bar'))


def test_constraint_get_parent():
    constraint = Constraint('foo')
    expression = Expression()

    constraint.set_parent(expression)

    assert expression == constraint.get_parent()


def test_constraint_get_parent_no_parent():
    with pytest.raises(
        FiqlObjectException,
        match=f"Parent must be of <class 'fiql_parser.expression.Expression'> not {type(None)}",
    ):
        Constraint('foo').get_parent()


def test_expression_has_constraint():
    expression = Expression()

    assert not expression.has_constraint()

    expression.add_element(Constraint('foo'))
    assert expression.has_constraint()


def test_expression_add_operator():
    expression = Expression()

    expression.add_operator(Operator(';'))
    assert Operator(';') == expression.operator

    new_expression = expression.add_operator(Operator(','))
    assert Operator(';') == expression.operator
    assert expression != new_expression
    assert Operator(',') == new_expression.operator


def test_expression_add_operator_invalid_operator():
    with pytest.raises(
        FiqlObjectException,
        match="<class 'fiql_parser.constraint.Constraint'> is not a valid element type",
    ):
        Expression().add_operator(Constraint('foo'))


def test_expression_add_element():
    expression = Expression()
    expression.add_element(Constraint('foo'))
    expression.add_element(Constraint('bar'))
    expression.add_element(Operator(';'))
    assert 'foo;bar' == str(expression)

    new_expression = expression.add_operator(Operator(','))
    assert Operator(';') == expression.operator
    assert expression != new_expression
    assert Operator(',') == new_expression.operator

    new_expression.add_element(Constraint('baa'))
    assert 'foo;bar,baa' == str(new_expression)


def test_expression_add_element_invalid_element():
    with pytest.raises(FiqlObjectException, match=f'{type("")} is not a valid element type'):
        Expression().add_element('foo')


def test_expression_create_nested_expression():
    expression = Expression()
    sub_expression = expression.create_nested_expression()
    sub_sub_expression = sub_expression.create_nested_expression()

    assert expression == sub_expression.get_parent()
    assert sub_expression == sub_sub_expression.get_parent()

    # TODO: Figure this bit out, it's not reallly testing anything.
    expression = Expression()
    expression.add_element(Constraint('foo'))
    sub_expression = expression.create_nested_expression()


def test_expression_get_parent():
    expression = Expression()

    sub_expression = expression.create_nested_expression()
    assert expression == sub_expression.get_parent()


def test_expression_get_parent_no_parent():
    with pytest.raises(
        FiqlObjectException,
        match=f"Parent must be of <class 'fiql_parser.expression.Expression'> not {type(None)}",
    ):
        Expression().get_parent()


def test_expression_fluent():
    expression = Expression().op_or(
        Constraint('foo', '==', 'bar'),
        Expression().op_and(Constraint('age', '=lt=', '55'), Constraint('age', '=gt=', '5')),
    )

    assert 'foo==bar,age=lt=55;age=gt=5' == str(expression)
    with pytest.raises(FiqlObjectException, match=f"{type('')} is not a valid element type"):
        Expression().op_or('foo')


def test_constraint_fluent():
    expression = Constraint('foo', '==', 'bar').op_or(
        Constraint('age', '=lt=', '55').op_and(Constraint('age', '=gt=', '5'))
    )

    assert 'foo==bar,age=lt=55;age=gt=5' == str(expression)


def test_to_string():
    sub_expression = Expression()
    sub_expression.add_element(Constraint('foo'))
    sub_expression.add_element(Operator(';'))
    sub_expression.add_element(Constraint('bar', '=gt=', '45'))
    expression = Expression()
    expression.add_element(Constraint('a', '==', 'wee'))
    expression.add_element(Operator(','))
    expression.add_element(sub_expression)
    expression.add_element(Operator(';'))
    expression.add_element(Constraint('key'))

    assert 'a==wee,foo;bar=gt=45;key' == str(expression)


def test_to_python():
    sub_expression = Expression()
    sub_expression.add_element(Constraint('foo'))
    sub_expression.add_element(Operator(';'))
    sub_expression.add_element(Constraint('bar', '=gt=', '45'))
    expression = Expression()
    expression.add_element(Constraint('a', '==', 'wee'))
    expression.add_element(Operator(','))
    expression.add_element(sub_expression)
    expression.add_element(Operator(';'))
    expression.add_element(Constraint('key'))

    assert [
        'OR',
        ('a', '==', 'wee'),
        ['AND', ['AND', ('foo', None, None), ('bar', '>', '45')], ('key', None, None)],
    ] == expression.to_python()


def test_expression_default_operator():
    expression = Expression()
    expression.add_element(Constraint('a', '==', 'wee'))
    expression.add_element(Constraint('bar', '=gt=', '45'))
    expression.add_element(Constraint('key'))

    assert 'a==wee;bar=gt=45;key' == str(expression)
    assert [
        'AND',
        ('a', '==', 'wee'),
        ('bar', '>', '45'),
        ('key', None, None),
    ] == expression.to_python()
