# -*- coding: utf-8 -*-
"""
Tests against the FIQL regex structures.
"""
import re

import pytest

from fiql_parser import constants as C


@pytest.mark.parametrize('pattern', ('###', '%A', '%G1', '%AAA',))
def test_pct_encoding_is_none(pattern):
    re_comp = re.compile(C.PCT_ENCODING_REGEX + '$')

    assert re_comp.match(pattern) is None


@pytest.mark.parametrize(
    'pattern',
    (
        '%5E',
        '%AF',
        '%02',
        '%C4',
        '%ad',
        '%2b',
        '%f1',
    ),
)
def test_pct_encoding_is_not_none(pattern):
    re_comp = re.compile(C.PCT_ENCODING_REGEX + '$')

    assert re_comp.match(pattern) is not None


@pytest.mark.parametrize(
    'pattern',
    (
        ':',
        '/',
        '?',
        '#',
        '[',
        ']',
        '@',
        '!',
        '$',
        '&',
        "'",
        '(',
        ')',
        '*',
        ',',
        ';',
        '=',
    ),
)
def test_unreserved_is_none(pattern):
    re_comp = re.compile(C.UNRESERVED_REGEX + r'+$')
    # Fail if we get even one reserved char
    assert re_comp.match(pattern) is None


@pytest.mark.parametrize(
    'pattern',
    (
        'POIUYTREWQASDFGHJKLMNBVCXZ',
        'qwertyuioplkjhgfdsazxcvbnm',
        '1234567890._-~',
    ),
)
def test_unreserved_is_not_none(pattern):
    re_comp = re.compile(C.UNRESERVED_REGEX + r'+$')

    assert re_comp.match(pattern) is not None


def test_fiql_delim_is_none():
    assert re.compile(C.FIQL_DELIM_REGEX + r'+$').match('=') is None


def test_fiql_delim_is_not_none():
    assert re.compile(C.FIQL_DELIM_REGEX + r'+$').match("!$'*+") is not None


@pytest.mark.parametrize(
    'pattern',
    (
        '=',
        '=gt',
    ),
)
def test_comparison_is_none(pattern):
    re_comp = re.compile(C.COMPARISON_REGEX + '$')

    # This test should fail per spec but that didn't make sense.
    assert re_comp.match(pattern) is None


@pytest.mark.parametrize(
    'pattern',
    (
        '==',
        '=gt=',
        '=ge=',
        '=lt=',
        '=le=',
        '!=',
        '$=',
        "'=",
        '*=',
        '+=',
    ),
)
def test_comparison_is_not_none(pattern):
    re_comp = re.compile(C.COMPARISON_REGEX + '$')

    assert re_comp.match(pattern) is not None


@pytest.mark.parametrize(
    'pattern',
    (
        '#',
        '!',
        '=',
        '',
    ),
)
def test_selector_is_none(pattern):
    re_comp = re.compile(C.SELECTOR_REGEX + '$')

    assert re_comp.match(pattern) is None


def test_selector_is_not_none():
    assert re.compile(C.SELECTOR_REGEX + '$').match('ABC%3Edef_34%04') is not None


@pytest.mark.parametrize(
    'pattern',
    (
        '?',
        '&',
        ',',
        ';',
        '',
    ),
)
def test_argument_is_none(pattern):
    re_comp = re.compile(C.ARGUMENT_REGEX + '$')

    assert re_comp.match(pattern) is None


def test_argument_is_not_none():
    assert re.compile(C.ARGUMENT_REGEX + '$').match("ABC%3Edef_34~.-%04!$'*+:=") is not None


@pytest.mark.parametrize(
    'value, expected',
    (
        ('foo==bar', ['', 'foo', 'o', '==bar', '==', '=', 'bar', 'r', ''],),
        ('foo=gt=bar', ['', 'foo', 'o', '=gt=bar', '=gt=', '=gt', 'bar', 'r', ''],),
        ('foo=le=bar', ['', 'foo', 'o', '=le=bar', '=le=', '=le', 'bar', 'r', ''],),
        ('foo!=bar', ['', 'foo', 'o', '!=bar', '!=', '!', 'bar', 'r', ''],),
        ('foo=bar', ['', 'foo', 'o', None, None, None, None, None, '=bar'],),
        ('foo==', ['', 'foo', 'o', None, None, None, None, None, '=='],),
        ('foo=', ['', 'foo', 'o', None, None, None, None, None, '='],),
        ('foo', ['', 'foo', 'o', None, None, None, None, None, ''],),
    )
)
def test_constraint(value, expected):
    re_comp = re.compile(C.CONSTRAINT_REGEX)

    assert re_comp.split(value, 1) == expected
