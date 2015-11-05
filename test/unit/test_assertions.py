import pytest

from pytest_check_mk import assertions



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
