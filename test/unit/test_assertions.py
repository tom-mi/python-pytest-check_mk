import pytest

from mock import call
from pytest_check_mk import assertions


def test_assert_inventory_and_check_works_with_check_output(mocker):
    check_output = '<<<arr>>>'

    fake_item = 'one more thing'
    fake_inventory = [(None, None), (fake_item, None), (None, 'default_params')]
    fake_check_result = (0, 'OK')
    fake_params = 42

    mocker.patch('pytest_check_mk.assertions.assert_well_formed_inventory')
    mocker.patch('pytest_check_mk.assertions.assert_well_formed_check_result')
    fake_check = mocker.Mock()
    fake_check.inventory = mocker.MagicMock(return_value=fake_inventory)
    fake_check.check = mocker.MagicMock(return_value=fake_check_result)
    fake_check.check_file.module.default_params = fake_params

    assertions.assert_inventory_and_check_works_with_check_output(fake_check, check_output)

    assertions.assert_well_formed_inventory.assert_called_once_with(fake_check, fake_inventory)
    fake_check.check.assert_has_calls([
        call(None, None, check_output),
        call(fake_item, None, check_output),
        call(None, fake_params, check_output),
    ])
    assertions.assert_well_formed_check_result.assert_has_calls([
        call(fake_check, fake_check_result),
        call(fake_check, fake_check_result),
        call(fake_check, fake_check_result),
    ])


@pytest.mark.parametrize('has_perfdata, result', [
    (False, (0, 'Everything fine')),
    (False, (1, 'Not so good anymore')),
    (False, (2, 'AAAAAAAARRRRGGGH')),
    (False, (3, 'WTF?')),
    (True,  (0, 'OK', [('foo', 1)])),
    (True,  (0, 'OK', [('foo', 1), ('bar', 5.)])),
])
def test_assert_well_formed_check_result_lives_for_correct_result(has_perfdata, result, mocker):
    mock_check = mocker.Mock()
    mock_check.has_perfdata = has_perfdata

    assertions.assert_well_formed_check_result(mock_check, result)


@pytest.mark.parametrize('has_perfdata, result', [
    (False, (-1, 'Foo')),
    (False, (4, 'Foo')),
    (False, ('foo', 'Foo')),
    (True,  (0, 'Foo')),
    (True,  (0, 'Foo', 'data')),
    (True,  (0, 'Foo', [('foo', 'broken')])),
])
def test_assert_well_formed_check_result_fails_for_wrong_result(has_perfdata, result, mocker):
    mock_check = mocker.Mock()
    mock_check.has_perfdata = has_perfdata

    with pytest.raises(AssertionError):
        assertions.assert_well_formed_check_result(mock_check, result)


@pytest.mark.parametrize('service_description, inventory', [
    ('Sample check', [(None, None)]),
    ('Sample check', [(None, 'sample_default_params')]),
    ('Sample check', []),
    ('Sample check for %s', []),
    ('Sample check for %s', [('foo', None)]),
])
def test_assert_well_formed_inventory_lives_for_correct_inventory(service_description, inventory, mocker):
    mock_check = mocker.Mock()
    mock_check.service_description = service_description

    assertions.assert_well_formed_inventory(mock_check, inventory)


@pytest.mark.parametrize('service_description, inventory', [
    ('Sample check', [(None, None), (None, None)]),
    ('Sample check', [('item', None)]),
    ('Sample check', [(None, 'non_existing_default_params')]),
    ('Sample check for %s', [(None, None)]),
])
def test_assert_well_formed_inventory_fail_for_wrong_inventory(service_description, inventory, mocker):
    mock_check = mocker.Mock()
    mock_check.service_description = service_description
    del mock_check.check_file.module.non_existing_default_params

    with pytest.raises(AssertionError):
        assertions.assert_well_formed_inventory(mock_check, inventory)


@pytest.mark.parametrize('entry', [
    (('foo', 1)),
    (('foo', 1, 2)),
    (('foo', 1, 2, 3)),
    (('foo', 1, 2, 3, 4)),
    (('foo', 1, 2, 3, 4, 5)),
    (('foo', .1)),
    (('foo', .1, .2)),
    (('foo', .1, .2, .3)),
    (('foo', .1, .2, .3, .4)),
    (('foo', .1, .2, .3, .4, .5)),
    (('foo', 1, '', 3)),
    (('foo', 1, 2, '', 4)),
    (('foo', 1, 2, 3, '', 5)),
])
def test_assert_well_formed_perfdata_entry_lives_for_correct_entry(entry):
    assertions.assert_well_formed_perfdata_entry(entry)


@pytest.mark.parametrize('entry', [
    (('foo',)),
    (('foo', 1, 2, 3, 4, 5, 6)),
    ((1, 1)),
    (('foo', 'foo')),
    (('foo', 1, 'foo')),
    (('foo', 1, 2, 'foo')),
    (('foo', 1, 2, 3, 'foo')),
    (('foo', 1, 2, 3, 4, 'foo')),
    (('foo', 1, 2, 3, 4, 5, 'foo')),
])
def test_assert_well_formed_perfdata_entry_fails_for_wrong_entry(entry):
    with pytest.raises(AssertionError):
        assertions.assert_well_formed_perfdata_entry(entry)



