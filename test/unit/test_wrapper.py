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
