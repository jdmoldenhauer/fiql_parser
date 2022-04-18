# -*- coding: utf-8 -*-
"""
Tests against the FIQL string parsing functions.
"""
import pytest

from fiql_parser import parse_str_to_expression
from fiql_parser import FiqlException
from fiql_parser.parser import iter_parse


def test_iter_parse():
    fiql_str = 'a==23;(b=gt=4,(c=ge=5;c=lt=15))'
    assert [
        ('', 'a', '==', '23'),
        (';(', 'b', '=gt=', '4'),
        (',(', 'c', '=ge=', '5'),
        (';', 'c', '=lt=', '15'),
        ('))', None, None, None),
    ] == list(iter_parse(fiql_str))


@pytest.mark.parametrize(
    'test_str, expected',
    (
        (
                'foo%24==bar%23+more',
                ('foo$', '==', 'bar# more'),
        ),
    ),
)
def test_parse_str_to_expression_pct_encoding(test_str, expected):
    expression = parse_str_to_expression(test_str)

    assert test_str == str(expression)
    assert expression.to_python() == expected


@pytest.mark.parametrize(
    'test_str, expected',
    (
        ('foo=gt=bar', ('foo', '>', 'bar'),),
        ('foo=le=bar', ('foo', '<=', 'bar'),),
        ('foo!=bar', ('foo', '!=', 'bar'),),
    ),
)
def test_parse_str_to_expression_constraint_only(test_str, expected):
    expression = parse_str_to_expression(test_str)
    assert test_str == str(expression)
    assert expression.to_python() == expected


@pytest.mark.parametrize(
    'test_str, expected_str, expected_py',
    (
        ('foo', 'foo', ('foo', None, None,),),
        ('((foo))', 'foo', ('foo', None, None,),),
    ),
)
def test_parse_str_to_expression_no_args(test_str, expected_str, expected_py):
    expression = parse_str_to_expression(test_str)

    assert expected_str == str(expression)
    assert expected_py == expression.to_python()


@pytest.mark.parametrize(
    'test_str, expected_py',
    (
        ('foo==bar;goo=gt=5', ['AND', ('foo', '==', 'bar'), ('goo', '>', '5')]),
        ('foo==bar;goo=gt=5;baa=lt=6', ['AND', ('foo', '==', 'bar'), ('goo', '>', '5'), ('baa', '<', '6')]),
        ('foo==bar,goo=lt=5', ['OR', ('foo', '==', 'bar'), ('goo', '<', '5')]),
        ('foo==bar,goo=lt=5,baa=gt=6', ['OR', ('foo', '==', 'bar'), ('goo', '<', '5'), ('baa', '>', '6')]),
    ),
)
def test_parse_str_to_expression_one_operation(test_str, expected_py):
    expression = parse_str_to_expression(test_str)

    assert str(expression) == test_str
    assert expression.to_python() == expected_py


@pytest.mark.parametrize(
    'test_str, expected_str, expected_py',
    (
        ('foo==bar,(goo=gt=5;goo=lt=10)',
         'foo==bar,goo=gt=5;goo=lt=10',
         ['OR', ('foo', '==', 'bar'), [
             'AND', ('goo', '>', '5'), ('goo', '<', '10')]]),
        ('(goo=gt=5;goo=lt=10),foo==bar',
         'goo=gt=5;goo=lt=10,foo==bar',
         ['OR', ['AND', ('goo', '>', '5'), ('goo', '<', '10')],
          ('foo', '==', 'bar')]),
        ('foo==bar;(goo=gt=5,goo=lt=10)',
         'foo==bar;(goo=gt=5,goo=lt=10)',
         ['AND', ('foo', '==', 'bar'), [
             'OR', ('goo', '>', '5'), ('goo', '<', '10')]]),
        ('(goo=gt=5,goo=lt=10);foo==bar',
         '(goo=gt=5,goo=lt=10);foo==bar',
         ['AND', ['OR', ('goo', '>', '5'), ('goo', '<', '10')],
          ('foo', '==', 'bar')]),
    ),
)
def test_parse_str_to_expression_explicit_nesting(test_str, expected_str, expected_py):
    expression = parse_str_to_expression(test_str)

    assert str(expression) == expected_str
    assert expression.to_python() == expected_py


@pytest.mark.parametrize(
    'test_str, expected_py',
    (
        ('foo==bar,goo=gt=5;goo=lt=10',
         ['OR', ('foo', '==', 'bar'), [
             'AND', ('goo', '>', '5'), ('goo', '<', '10')]]),
        ('goo=gt=5;goo=lt=10,foo==bar',
         ['OR', ['AND', ('goo', '>', '5'), ('goo', '<', '10')],
          ('foo', '==', 'bar')]),
    ),
)
def test_parse_str_to_expression_implicit_nesting(test_str, expected_py):
    expression = parse_str_to_expression(test_str)

    assert str(expression) == test_str
    assert expression.to_python() == expected_py

    fiql_strings = [
        ('foo==bar,goo=gt=5;goo=lt=10',
         ['OR', ('foo', '==', 'bar'), [
             'AND', ('goo', '>', '5'), ('goo', '<', '10')]]),
        ('goo=gt=5;goo=lt=10,foo==bar',
         ['OR', ['AND', ('goo', '>', '5'), ('goo', '<', '10')],
          ('foo', '==', 'bar')]),
    ]
    for test_str, expected_py in fiql_strings:
        expression = parse_str_to_expression(test_str)
        assert test_str == str(expression)
        assert expected_py == expression.to_python()


@pytest.mark.parametrize(
    'not_fiql_string',
    (
        'foo=bar',
        'foo==',
        'foo=',
        ';;foo',
        '(foo)(bar)',
        '(foo==bar',
        'foo==bar(foo==bar)',
        ';foo==bar',
        'foo==bar;,foo==bar',
    )
)
def test_parse_str_to_expression_failure(not_fiql_string):
    with pytest.raises(FiqlException):
        parse_str_to_expression(not_fiql_string)
