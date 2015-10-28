import textwrap
import types

import pytest

from pytest_check_mk import MissingFileError
from pytest_check_mk import file_loader


@pytest.fixture
def example_check(tmpdir):
    check_file = tmpdir.mkdir('checks').join('example')

    def fill_file(content):
        check_file.open('w').write(textwrap.dedent(content))
        return str(check_file)

    return fill_file


def test_check_module_from_source_fails_on_missing_file(tmpdir):
    name = 'foo'
    path = str(tmpdir.join('foo'))

    with pytest.raises(MissingFileError):
        file_loader.check_module_from_source(name, path)


def test_check_module_from_source_fails_on_syntax_error(example_check):
    name = 'foo'
    path = example_check('''
        print("foo
    ''')

    with pytest.raises(SyntaxError):
        file_loader.check_module_from_source(name, path)


def test_check_module_from_source_contains_empty_dicts_and_lists(example_check):
    name = 'foo'
    path = example_check('')
    expected_dicts = [
        'check_info', 'checkgroup_of', 'check_includes', 'precompile_params',
        'check_default_levels', 'factory_settings',
        'snmp_info', 'snmp_scan_functions', 'active_check_info',
        'special_agent_info',
    ]
    expected_lists = [
        'check_config_variables',
    ]

    module = file_loader.check_module_from_source(name, path)

    for dict_name in expected_dicts:
        assert hasattr(module, dict_name)
        assert getattr(module, dict_name) == {}

    for list_name in expected_lists:
        assert hasattr(module, list_name)
        assert getattr(module, list_name) == []


def test_check_module_from_source_can_fill_predefined_dicts_and_lists(example_check):
    name = 'foo'
    path = example_check('''
        check_info['foo.bar'] = {'key': 'value'}
        check_config_variables.append('another_item')
    ''')

    module = file_loader.check_module_from_source(name, path)

    assert module.check_info['foo.bar'] == {'key': 'value'}
    assert module.check_config_variables == ['another_item']


def test_check_module_from_source_contains_functions(example_check):
    name = 'foo'
    path = example_check('''
        def calculate_square(value):
            return value * value
    ''')

    module = file_loader.check_module_from_source(name, path)

    assert hasattr(module, 'calculate_square')
    assert type(module.calculate_square) == types.FunctionType
    assert module.calculate_square(5) == 25


def test_check_module_from_source_contains_variables(example_check):
    name = 'foo'
    path = example_check('''
        some_value = 5
    ''')

    module = file_loader.check_module_from_source(name, path)

    assert hasattr(module, 'some_value')
    assert module.some_value == 5
