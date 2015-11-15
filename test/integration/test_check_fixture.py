import pytest
import textwrap


@pytest.fixture
def example_check(testdir):
    check_file = testdir.mkdir('checks').join('example')

    def fill_file(content):
        check_file.open('w').write(textwrap.dedent(content))

    return fill_file


def test_checks_fixture_fails_on_missing_check_specification(testdir):
    testdir.makepyfile('''
        def test_foo(checks):
            pass
    ''')

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*UsageError: Please specify the check to test*
        *UsageError
    ''')


def test_checks_fixture_returns_check_file_wrapper(testdir, example_check, monkeypatch):
    example_check('')
    testdir.makepyfile('''
        from pytest_check_mk.wrapper import CheckWrapper, CheckFileWrapper

        test_for = 'example'

        def test_foo(checks):
            assert isinstance(checks, CheckFileWrapper)
            assert isinstance(checks['example'], CheckWrapper)
    ''')

    result = testdir.runpytest()

    assert result.ret == 0


def test_check_calls_parse_info(testdir, example_check, mocker):
    import pytest_check_mk.wrapper

    mocker.patch('pytest_check_mk.wrapper.parse_info', return_value=('example', 'foobar'))

    example_check('''
        check_info['example.foo'] = {'check_function': lambda x, y, z: (x, y, z)}
    ''')

    testdir.makepyfile('''
        test_for = 'example'

        def test_foo(checks):
            assert checks['example.foo'].check('arg1', 'arg2', '<<<example>>>\\na b') == ('arg1', 'arg2', 'foobar')
    ''')

    result = testdir.runpytest()

    pytest_check_mk.wrapper.parse_info.assert_called_once_with('<<<example>>>\na b')
    assert result.ret == 0
