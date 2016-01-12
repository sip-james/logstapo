import itertools
import re

import pytest

from logstapo import util


@pytest.mark.parametrize(('regexps', 'string', 'expected'), (
    ('foo', 'bar', False),
    ('f.o', 'foo', True),
    (['foo', 'bar'], 'bar', True),
    (['foo', 'baz'], 'bar', False),
    (['foo', '(b)ar', 'b(a)r'], 'bar', 'b'),
))
def test_try_match(regexps, string, expected):
    regexps = re.compile(regexps) if isinstance(regexps, str) else list(map(re.compile, regexps))
    match = util.try_match(regexps, string)
    if not expected:
        assert match is None
    elif isinstance(expected, str):
        assert match.groups()[0] == expected
    else:
        assert match is not None


@pytest.mark.parametrize('debug', (True, False))
def test_debug_echo(mocker, debug):
    mocker.patch('logstapo.config.current_config', {'debug': debug})
    secho = mocker.patch('logstapo.util.click.secho')
    util.debug_echo('test')
    assert secho.called == debug


@pytest.mark.parametrize(('level', 'verbosity', 'debug'), itertools.product((1, 2), (0, 1, 2), (True, False)))
def test_verbose_echo(mocker, level, verbosity, debug):
    mocker.patch('logstapo.config.current_config', data={'debug': debug, 'verbosity': verbosity})
    secho = mocker.patch('logstapo.util.click.secho')
    util.verbose_echo(level, 'test')
    assert secho.called == (debug or (level <= verbosity))


def test_warning_echo(mocker):
    secho = mocker.patch('logstapo.util.click.secho')
    util.warning_echo('test')
    assert secho.called


def test_error_echo(mocker):
    secho = mocker.patch('logstapo.util.click.secho')
    util.error_echo('test')
    assert secho.called


@pytest.mark.parametrize(('text', 'chars', 'expected'), (
    ('test', '-', '----'),
    ('test', '-=', '-=-='),
    ('t', '-=', '-')
))
def test_underlines(text, chars, expected):
    assert util.underlined(text, chars) == [text, expected]


@pytest.mark.parametrize(('value', 'collection_type', 'result'), (
    ('test', list, ['test']),
    ('test', set, {'test'}),
    ('test', tuple, ('test',)),
    ({'test'}, list, ['test']),
    (('test',), set, {'test'}),
    (['test'], tuple, ('test',)),
))
def test_ensure_collection(value, collection_type, result):
    assert util.ensure_collection(value, collection_type) == result