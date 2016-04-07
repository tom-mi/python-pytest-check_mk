import pytest

from pytest_check_mk import wrapper


@pytest.mark.parametrize('check_output, expected_section_name, expected_info', [
    ('<<<foo>>>',              'foo', []),
    ('<<<foo>>>\na bc',        'foo', [['a', 'bc']]),
    ('<<<foo>>>\na bc\n',      'foo', [['a', 'bc']]),
    ('<<<bar>>>\na bc\nd',     'bar', [['a', 'bc'], ['d']]),
    ('<<<bar>>>\na   b',       'bar', [['a', 'b']]),
    ('<<<bar:sep(48)>>>\n101', 'bar', [['1', '1']]),
])
def test_parse_info(check_output, expected_section_name, expected_info):
    section_name, info = wrapper.parse_info(check_output)

    assert section_name == expected_section_name
    assert info == expected_info


@pytest.fixture
def checks(mocker):
    name = 'foo'
    module = mocker.Mock()
    module.check_info = {}
    return wrapper.CheckFileWrapper(name, module)


def test_has_no_perfdata(checks):
    checks.module.check_info['foo.bar'] = {}

    assert not checks['foo.bar'].has_perfdata


def test_has_perfdata(checks):
    checks.module.check_info['foo.bar'] = {'has_perfdata': True}

    assert checks['foo.bar'].has_perfdata


def test_service_description(checks):
    checks.module.check_info['foo.bar'] = {'service_description': 'Foo for %s'}

    assert checks['foo.bar'].service_description == 'Foo for %s'


def test_inventory_fails_on_wrong_section_header(checks):
    checks.module.check_info['foo.bar'] = {}

    with pytest.raises(ValueError) as exc:
        checks['foo.bar'].inventory('<<<arrr>>>\n1 2')

    assert 'Wrong section name in test data' in str(exc.value)


def test_inventory_fails_on_invalid_section_header(checks):
    checks.module.check_info['foo.bar'] = {}

    with pytest.raises(ValueError) as exc:
        checks['foo.bar'].inventory('<<<foo\n1 2')

    assert 'Invalid header in test data' in str(exc.value)


def test_inventory_calls_parse_info_and_passes_result_to_inventory(checks, mocker):
    check_output = '<<<foo>>>\n1 2 3'
    fake_parsed_info = mocker.Mock()

    mock_inventory = mocker.Mock()
    mock_parse_info = mocker.Mock(return_value=('foo', fake_parsed_info))
    checks.module.check_info['foo.bar'] = {'inventory_function': mock_inventory}
    mocker.patch('pytest_check_mk.wrapper.parse_info', mock_parse_info)

    checks['foo.bar'].inventory(check_output)

    mock_parse_info.assert_called_with(check_output)
    mock_inventory.assert_called_with(fake_parsed_info)


def test_inventory_calls_inventory_and_returns_result(checks, mocker):
    check_output = '<<<foo>>>\n1 2 3'
    return_value = mocker.Mock()

    mock_inventory = mocker.Mock(return_value=return_value)
    checks.module.check_info['foo.bar'] = {'inventory_function': mock_inventory}

    assert checks['foo.bar'].inventory(check_output) == return_value
    mock_inventory.assert_called_with([['1', '2', '3']])


def test_check_calls_parse_info_and_passes_result_to_check(checks, mocker):
    check_output = '<<<foo>>>\n1 2 3'
    fake_parsed_info = mocker.Mock()

    mock_check = mocker.Mock(return_value=(0, 'mock'))
    mock_parse_info = mocker.Mock(return_value=('foo', fake_parsed_info))
    checks.module.check_info['foo.bar'] = {'check_function': mock_check}
    mocker.patch('pytest_check_mk.wrapper.parse_info', mock_parse_info)

    checks['foo.bar'].check(None, None, check_output)

    mock_parse_info.assert_called_with(check_output)
    mock_check.assert_called_with(None, None, fake_parsed_info)


def test_check_calls_check_and_returns_result(checks, mocker):
    check_output = '<<<foo>>>\n1 2 3'
    return_value = (0, 'mock')
    item = 'item'
    params = {'key': 'params'}

    mock_check = mocker.Mock(return_value=return_value)
    checks.module.check_info['foo.bar'] = {'check_function': mock_check}

    assert checks['foo.bar'].check(item, params, check_output) == return_value
    mock_check.assert_called_with(item, params, [['1', '2', '3']])


def test_check_handles_single_yield_in_check(checks):
    check_output = '<<<foo>>>\n1 2 3'
    return_value = (0, 'everything ok')
    item = 'item'
    params = {'key': 'params'}

    def mock_check(*args):
        yield return_value

    checks.module.check_info['foo.bar'] = {'check_function': mock_check}

    assert checks['foo.bar'].check(item, params, check_output) == return_value


def test_check_handles_multiple_yields_in_check(checks):
    check_output = '<<<foo>>>\n1 2 3'
    return_values = [(0, 'everything ok'), (2, 'everything broken', ['perf-data'])]
    item = 'item'
    params = {'key': 'params'}
    expected_result = (2, 'everything ok, everything broken(!!)', ['perf-data'])

    def mock_check(*args):
        yield return_values[0]
        yield return_values[1]

    checks.module.check_info['foo.bar'] = {'check_function': mock_check}

    assert checks['foo.bar'].check(item, params, check_output) == expected_result
